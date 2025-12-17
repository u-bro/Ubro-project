import pytest


@pytest.mark.asyncio
async def test_rides_create_and_status_change(client):
    # Ensure a user exists
    u = await client.post("/api/v1/users/2001", json={
        "telegram_id": 2001,
        "first_name": "Client",
        "username": "client2001"
    })
    assert u.status_code == 200, u.text
    user_id = u.json()["id"]

    # Create ride
    r = await client.post("/api/v1/rides", json={
        "client_id": user_id,
        "pickup_address": "Point A",
        "dropoff_address": "Point B"
    })
    assert r.status_code == 201, r.text
    ride = r.json()
    ride_id = ride["id"]
    assert ride.get("status") in ("requested", None)

    # Change status to canceled by client (allowed from requested)
    ch = await client.post(f"/api/v1/rides/{ride_id}/status", json={
        "to_status": "canceled",
        "actor_role": "client",
        "reason": "user canceled"
    })
    assert ch.status_code == 200, ch.text
    ride2 = ch.json()
    assert ride2["status"] == "canceled"
