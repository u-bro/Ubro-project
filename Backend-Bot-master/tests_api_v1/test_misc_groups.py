import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("path", [
    "/api/v1/driver-profiles?page=1&page_size=1",
    "/api/v1/driver-documents?page=1&page_size=1",
    "/api/v1/phone-verifications?page=1&page_size=1",
    "/api/v1/commissions?page=1&page_size=1",
    "/api/v1/driver-locations?page=1&page_size=1",
    "/api/v1/chat-messages?page=1&page_size=1",
    "/api/v1/transactions?page=1&page_size=1",
])
async def test_smoke_list_endpoints(client, path):
    r = await client.get(path)
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        data = r.json()
        assert isinstance(data, list)
