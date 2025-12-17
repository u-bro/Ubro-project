import pytest


@pytest.mark.asyncio
async def test_health_ok(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, dict)
    assert body.get("status") in ("ok", None)
