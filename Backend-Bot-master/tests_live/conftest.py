"""
Conftest для тестирования на реальном сервере (localhost:5000).
Не поднимает тестовую БД, подключается к работающему приложению.
"""
import pytest
import pytest_asyncio
import httpx
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def base_url():
    """URL реального сервера"""
    return "http://localhost:5000"


@pytest_asyncio.fixture(scope="function")
async def client(base_url):
    """HTTP клиент для работы с реальным сервером"""
    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=30.0,
        headers={"Content-Type": "application/json"}
    ) as ac:
        yield ac
