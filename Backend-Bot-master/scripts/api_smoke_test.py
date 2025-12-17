import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, List, Tuple, Optional
import os
from datetime import datetime


def http_request(method: str, url: str, headers: Dict[str, str], data: Optional[bytes]) -> Tuple[int, float, str]:
    req = urllib.request.Request(url=url, method=method.upper(), headers=headers)
    if data is not None:
        req.data = data
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read()
            dt = time.time() - start
            try:
                text = body.decode("utf-8", errors="replace")
            except Exception:
                text = "<binary>"
            return resp.getcode(), dt, text[:500]
    except urllib.error.HTTPError as e:
        dt = time.time() - start
        try:
            text = e.read().decode("utf-8", errors="replace")
        except Exception:
            text = str(e)
        return e.code, dt, text[:500]
    except Exception as e:
        dt = time.time() - start
        return -1, dt, f"ERROR: {e}"


def fetch_openapi(base_url: str) -> Dict[str, Any]:
    url = base_url.rstrip("/") + "/openapi.json"
    req = urllib.request.Request(url=url, method="GET", headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        if resp.getcode() != 200:
            raise RuntimeError(f"Failed to fetch openapi.json ({resp.getcode()})")
        raw = resp.read()
        text = raw.decode("utf-8", errors="replace")
        return json.loads(text)


def resolve_ref(ref: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"External refs not supported: {ref}")
    parts = ref.lstrip("#/").split("/")
    node: Any = spec
    for p in parts:
        node = node[p]
    return node


def build_sample_from_schema(schema: Dict[str, Any], spec: Dict[str, Any], depth: int = 0) -> Any:
    if depth > 5:
        return None
    if not schema:
        return None
    if "$ref" in schema:
        resolved = resolve_ref(schema["$ref"], spec)
        return build_sample_from_schema(resolved, spec, depth + 1)
    for key in ("oneOf", "anyOf"):
        if key in schema and isinstance(schema[key], list) and schema[key]:
            return build_sample_from_schema(schema[key][0], spec, depth + 1)
    if "allOf" in schema and isinstance(schema["allOf"], list) and schema["allOf"]:
        merged = {}
        for sub in schema["allOf"]:
            sub_res = build_sample_from_schema(sub, spec, depth + 1)
            if isinstance(sub_res, dict):
                merged.update(sub_res)
        return merged or None
    t = schema.get("type")
    if not t and "properties" in schema:
        t = "object"
    if t == "object":
        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        result: Dict[str, Any] = {}
        for name, prop in props.items():
            if name in required:
                result[name] = build_sample_from_schema(prop, spec, depth + 1)
        if not result:
            count = 0
            for name, prop in props.items():
                result[name] = build_sample_from_schema(prop, spec, depth + 1)
                count += 1
                if count >= 2:
                    break
        return result
    if t == "array":
        item_schema = schema.get("items", {})
        return [build_sample_from_schema(item_schema, spec, depth + 1)]
    if t == "integer":
        return 1
    if t == "number":
        return 1.0
    if t == "boolean":
        return False
    if t == "string":
        fmt = schema.get("format")
        if fmt == "date-time":
            return datetime.utcnow().isoformat() + "Z"
        return "string"
    return None


def build_path_with_params(base_url: str, path: str, parameters: List[Dict[str, Any]]) -> str:
    url = base_url.rstrip("/") + path
    for p in parameters:
        if p.get("in") == "path":
            name = p["name"]
            schema = p.get("schema", {})
            sample = build_sample_from_schema(schema, {"components": {}, "paths": {}}, 0)
            if sample is None:
                sample = 1
            url = url.replace("{" + name + "}", urllib.parse.quote(str(sample)))
    q = []
    for p in parameters:
        if p.get("in") == "query":
            name = p["name"]
            schema = p.get("schema", {})
            if "default" in schema:
                q.append((name, str(schema["default"])))
    if q:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(q)
    return url


def run_smoke(base_url: str, token: Optional[str]) -> Dict[str, Any]:
    spec = fetch_openapi(base_url)
    results: List[Dict[str, Any]] = []
    global_headers = {"Accept": "application/json"}
    if token:
        global_headers["Authorization"] = token
    paths: Dict[str, Any] = spec.get("paths", {})
    for path, ops in paths.items():
        for method, op in ops.items():
            method_u = method.upper()
            if method_u not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                continue
            parameters = op.get("parameters", [])
            url = build_path_with_params(base_url, path, parameters)
            body_bytes = None
            headers = dict(global_headers)
            if method_u in ("POST", "PUT", "PATCH"):
                req_body = op.get("requestBody")
                if req_body:
                    content = req_body.get("content", {}).get("application/json")
                    if content:
                        schema = content.get("schema") or {}
                        sample = build_sample_from_schema(schema, spec, 0)
                        if sample is None:
                            sample = {}
                        body_bytes = json.dumps(sample).encode("utf-8")
                        headers["Content-Type"] = "application/json"
            code, dt, body = http_request(method_u, url, headers, body_bytes)
            results.append({
                "method": method_u,
                "path": path,
                "url": url,
                "status": code,
                "time_sec": round(dt, 3),
                "snippet": body,
            })
    return {
        "base_url": base_url,
        "ts": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "total": len(results),
            "ok": sum(1 for r in results if isinstance(r.get("status"), int) and 200 <= r["status"] < 400),
            "errors": sum(1 for r in results if not isinstance(r.get("status"), int) or r["status"] >= 400 or r["status"] < 0),
        },
        "results": results,
    }


def main():
    base_url = os.environ.get("API_BASE_URL") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not base_url:
        print("Usage: python scripts/api_smoke_test.py <BASE_URL> [AUTH_TOKEN]")
        print("       API_BASE_URL env var is also supported")
        sys.exit(2)
    token = os.environ.get("API_AUTH_TOKEN") or (sys.argv[2] if len(sys.argv) > 2 else None)
    report = run_smoke(base_url, token)
    os.makedirs("scripts/reports", exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_json = f"scripts/reports/smoke_report_{ts}.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("Base:", report["base_url"])
    print("When:", report["ts"])
    print("Summary:", report["summary"])
    print(f"Saved: {out_json}")
    for r in report["results"][:20]:
        print(f"{r['status']:>3} {r['time_sec']:>5.2f}s {r['method']:>6} {r['url']}")


if __name__ == "__main__":
    main()
