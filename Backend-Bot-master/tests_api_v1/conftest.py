import os
import subprocess
import time
import shutil
import pytest
import pytest_asyncio
import sys
from pathlib import Path
import httpx
from httpx import ASGITransport

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Ensure pytest mode uses .env-test
os.environ.setdefault("PYTEST_RUNNING", "1")

from app.backend.main import app  # noqa: E402


def _run_compose(*args: str) -> None:
    """Prefer 'docker compose', fallback to legacy 'docker-compose'."""
    if shutil.which("docker"):
        try:
            subprocess.run(["docker", "compose", *args], check=True)
            return
        except Exception:
            pass
    # fallback
    subprocess.run(["docker-compose", *args], check=True)


@pytest.fixture(scope="session", autouse=True)
def _db_container_and_migrations():
    # Start test Postgres via compose
    _run_compose("-f", "docker-compose-tests.yml", "up", "-d", "--build")
    # Simple wait for DB to be ready
    time.sleep(3)
    # Run migrations
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    # Keep DB up for the entire session to avoid teardown hangs
    yield


@pytest_asyncio.fixture()
async def client():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver", timeout=15.0) as c:
        yield c
