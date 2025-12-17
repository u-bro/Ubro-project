import pytest


@pytest.mark.asyncio
async def test_users_create_and_list(client):
    # create or get by telegram id
    u = await client.post("/api/v1/users/1001", json={
        "telegram_id": 1001,
        "first_name": "Vlad",
        "username": "vlad1001"
    })
    assert u.status_code == 200, u.text
    user = u.json()
    assert user["id"] > 0
    # list
    lst = await client.get("/api/v1/users?page=1&page_size=1")
    assert lst.status_code == 200
    assert isinstance(lst.json(), list)
    # update
    uid = user["id"]
    up = await client.put(f"/api/v1/users/{uid}", json={
        "id": uid,
        "telegram_id": 1001,
        "first_name": "Vladimir",
        "username": "vlad1001",
        "balance": 0.0
    })
    assert up.status_code == 200
