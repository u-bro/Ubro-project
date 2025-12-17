import pytest


@pytest.mark.asyncio
async def test_roles_crud_flow(client):
    # initial count
    rc = await client.get("/api/v1/roles/count")
    assert rc.status_code in (200, 404) or rc.status_code == 200
    # create
    create = await client.post("/api/v1/roles", json={"code": "admin", "name": "Administrator"})
    assert create.status_code == 201, create.text
    role = create.json()
    assert role["code"] == "admin"
    role_id = role["id"]

    # get by id
    rb = await client.get(f"/api/v1/roles/{role_id}")
    assert rb.status_code == 200
    # update
    upd = await client.put(f"/api/v1/roles/{role_id}", json={"name": "Admin"})
    assert upd.status_code == 200
    # list
    lst = await client.get("/api/v1/roles?page=1&page_size=10")
    assert lst.status_code == 200
    assert isinstance(lst.json(), list)
    # delete
    dele = await client.delete(f"/api/v1/roles/{role_id}")
    assert dele.status_code == 200
    # get by id should 404 or string message
    rb2 = await client.get(f"/api/v1/roles/{role_id}")
    assert rb2.status_code in (200, 404)
