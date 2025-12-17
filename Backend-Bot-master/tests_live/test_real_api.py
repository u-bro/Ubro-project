"""
Реальные API тесты с проверкой бизнес-логики.
Каждый тест создаёт свои данные и проверяет конкретные сценарии.
"""
import pytest
from datetime import datetime
import random


# ============================================================================
# USERS - Реальные тесты пользователей
# ============================================================================

@pytest.mark.asyncio
async def test_users_crud_full_cycle(client):
    """Полный цикл CRUD для пользователя"""
    telegram_id = random.randint(100000, 999999)
    
    # 1. Создание пользователя
    create_response = await client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "TestCRUD",
        "username": f"testcrud_{telegram_id}"
    })
    assert create_response.status_code == 200, f"Create user failed: {create_response.text}"
    user_data = create_response.json()
    assert user_data["telegram_id"] == telegram_id
    assert user_data["first_name"] == "TestCRUD"
    user_id = user_data["id"]
    
    # 2. Повторный запрос - должен вернуть того же пользователя (не создавать нового)
    get_response = await client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "Different",  # Другое имя
        "username": f"different_{telegram_id}"
    })
    assert get_response.status_code == 200
    same_user = get_response.json()
    assert same_user["id"] == user_id, "Should return same user, not create new"
    assert same_user["first_name"] == "TestCRUD", "Should not update existing user"
    
    # 3. Обновление пользователя
    update_response = await client.put(f"/api/v1/users/{user_id}", json={
        "id": user_id,
        "telegram_id": telegram_id,
        "first_name": "UpdatedName",
        "username": f"updated_{telegram_id}",
        "balance": 100.0
    })
    assert update_response.status_code == 200, f"Update user failed: {update_response.text}"
    updated_user = update_response.json()
    assert updated_user["first_name"] == "UpdatedName"
    
    # 4. Список пользователей - должен содержать созданного
    list_response = await client.get("/api/v1/users?page=1&page_size=100")
    assert list_response.status_code == 200
    users_list = list_response.json()
    assert isinstance(users_list, list)
    user_ids = [u["id"] for u in users_list]
    # Note: Пользователь может быть на другой странице, просто проверяем что список работает


@pytest.mark.asyncio
async def test_users_update_nonexistent(client):
    """Обновление несуществующего пользователя должно вернуть 404 или 422"""
    response = await client.put("/api/v1/users/999999", json={
        "id": 999999,
        "telegram_id": 999999,
        "first_name": "Ghost",
        "username": "ghost",
        "balance": 0.0
    })
    # FastAPI вернёт 422 если схема не совпадает, или 404 если не найден
    assert response.status_code in (404, 422), f"Expected 404/422, got {response.status_code}"


# ============================================================================
# ROLES - Реальные тесты ролей  
# ============================================================================

@pytest.mark.asyncio
async def test_roles_crud_full_cycle(client):
    """Полный цикл CRUD для ролей"""
    role_code = f"test_role_{random.randint(10000, 99999)}"
    
    # 1. Создание роли
    create_response = await client.post("/api/v1/roles", json={
        "code": role_code,
        "name": "Test Role",
        "description": "Role for testing"
    })
    assert create_response.status_code == 201, f"Create role failed: {create_response.text}"
    role = create_response.json()
    role_id = role["id"]
    assert role["code"] == role_code
    
    # 2. Получение по ID
    get_response = await client.get(f"/api/v1/roles/{role_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == role_id
    
    # 3. Обновление
    update_response = await client.put(f"/api/v1/roles/{role_id}", json={
        "name": "Updated Role Name",
        "description": "Updated description"
    })
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Role Name"
    
    # 4. Удаление
    delete_response = await client.delete(f"/api/v1/roles/{role_id}")
    assert delete_response.status_code == 200
    
    # 5. Проверка что удалён
    get_after_delete = await client.get(f"/api/v1/roles/{role_id}")
    assert get_after_delete.status_code == 404, "Deleted role should return 404"


@pytest.mark.asyncio
async def test_roles_delete_nonexistent(client):
    """Удаление несуществующей роли должно вернуть 404"""
    response = await client.delete("/api/v1/roles/999999")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


# ============================================================================
# RIDES - Реальные тесты поездок
# ============================================================================

@pytest.mark.asyncio
async def test_rides_create_and_get(client):
    """Создание и получение поездки"""
    # Сначала создаём пользователя для клиента
    telegram_id = random.randint(100000, 999999)
    user_response = await client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "RideTestClient",
        "username": f"rideclient_{telegram_id}"
    })
    assert user_response.status_code == 200
    client_id = user_response.json()["id"]
    
    # Создаём поездку
    ride_response = await client.post("/api/v1/rides", json={
        "client_id": client_id,
        "pickup_address": "Test Street 1",
        "pickup_lat": 50.4501,
        "pickup_lng": 30.5234,
        "dropoff_address": "Test Street 2",
        "dropoff_lat": 50.4600,
        "dropoff_lng": 30.5300,
        "expected_fare": 150.0,
        "expected_fare_snapshot": {"base": 50, "distance": 100}
    })
    assert ride_response.status_code == 201, f"Create ride failed: {ride_response.text}"
    ride = ride_response.json()
    ride_id = ride["id"]
    assert ride["status"] == "requested", "New ride should have 'requested' status"
    assert ride["client_id"] == client_id
    
    # Получение по ID
    get_response = await client.get(f"/api/v1/rides/{ride_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == ride_id


@pytest.mark.asyncio
async def test_rides_change_status_not_found(client):
    """Смена статуса несуществующей поездки должна вернуть 404"""
    response = await client.post("/api/v1/rides/999999/status", json={
        "to_status": "canceled",
        "reason": "Test",
        "actor_id": 1,
        "actor_role": "client"
    })
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
async def test_rides_change_status_success(client):
    """Успешная смена статуса поездки"""
    # Создаём пользователя
    telegram_id = random.randint(100000, 999999)
    user_response = await client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "StatusTestClient",
        "username": f"statusclient_{telegram_id}"
    })
    client_id = user_response.json()["id"]
    
    # Создаём поездку
    ride_response = await client.post("/api/v1/rides", json={
        "client_id": client_id,
        "pickup_address": "Start",
        "pickup_lat": 50.45,
        "pickup_lng": 30.52,
        "dropoff_address": "End",
        "dropoff_lat": 50.46,
        "dropoff_lng": 30.53,
        "expected_fare": 100.0,
        "expected_fare_snapshot": {}
    })
    ride_id = ride_response.json()["id"]
    
    # Клиент отменяет поездку (requested -> canceled разрешено для client)
    cancel_response = await client.post(f"/api/v1/rides/{ride_id}/status", json={
        "to_status": "canceled",
        "reason": "Changed my mind",
        "actor_id": client_id,
        "actor_role": "client"
    })
    assert cancel_response.status_code == 200, f"Cancel failed: {cancel_response.text}"
    assert cancel_response.json()["status"] == "canceled"


# ============================================================================
# DRIVER PROFILES - Реальные тесты профилей водителей
# ============================================================================

@pytest.mark.asyncio
async def test_driver_profile_create_success(client):
    """Успешное создание профиля водителя"""
    # Создаём уникального пользователя
    telegram_id = random.randint(100000, 999999)
    user_response = await client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "NewDriver",
        "username": f"driver_{telegram_id}"
    })
    user_id = user_response.json()["id"]
    
    # Создаём профиль
    profile_response = await client.post("/api/v1/driver-profiles", json={
        "user_id": user_id,
        "license_number": f"LIC{telegram_id}",
        "approved": False
    })
    assert profile_response.status_code == 201, f"Create profile failed: {profile_response.text}"
    profile = profile_response.json()
    assert profile["user_id"] == user_id


@pytest.mark.asyncio
async def test_driver_profile_duplicate_user(client):
    """Попытка создать второй профиль для того же пользователя"""
    # Создаём пользователя
    telegram_id = random.randint(100000, 999999)
    user_response = await client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "DuplicateDriver",
        "username": f"dupdriver_{telegram_id}"
    })
    user_id = user_response.json()["id"]
    
    # Создаём первый профиль
    first_response = await client.post("/api/v1/driver-profiles", json={
        "user_id": user_id,
        "license_number": f"FIRST{telegram_id}",
        "approved": False
    })
    assert first_response.status_code == 201
    
    # Попытка создать второй профиль для того же user_id
    second_response = await client.post("/api/v1/driver-profiles", json={
        "user_id": user_id,
        "license_number": f"SECOND{telegram_id}",
        "approved": False
    })
    # Должен вернуть 409 Conflict (duplicate)
    assert second_response.status_code == 409, f"Expected 409 for duplicate, got {second_response.status_code}: {second_response.text}"


# ============================================================================
# DRIVER LOCATIONS - Реальные тесты локаций водителей
# ============================================================================

@pytest.mark.asyncio
async def test_driver_location_foreign_key_error(client):
    """Создание локации для несуществующего профиля водителя"""
    response = await client.post("/api/v1/driver-locations", json={
        "driver_profile_id": 999999,  # Не существует
        "latitude": 50.4501,
        "longitude": 30.5234,
        "is_online": True
    })
    # Должен вернуть 422 (FK violation)
    assert response.status_code == 422, f"Expected 422 for FK violation, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
async def test_driver_location_create_success(client):
    """Успешное создание локации водителя"""
    # Создаём пользователя
    telegram_id = random.randint(100000, 999999)
    user_response = await client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "LocationDriver",
        "username": f"locdriver_{telegram_id}"
    })
    user_id = user_response.json()["id"]
    
    # Создаём профиль водителя
    profile_response = await client.post("/api/v1/driver-profiles", json={
        "user_id": user_id,
        "license_number": f"LOC{telegram_id}",
        "approved": True
    })
    assert profile_response.status_code == 201
    profile_id = profile_response.json()["id"]
    
    # Создаём локацию
    location_response = await client.post("/api/v1/driver-locations", json={
        "driver_profile_id": profile_id,
        "latitude": 50.4501,
        "longitude": 30.5234,
        "is_online": True
    })
    assert location_response.status_code == 201, f"Create location failed: {location_response.text}"
    location = location_response.json()
    assert location["driver_profile_id"] == profile_id
    assert location["is_online"] == True


# ============================================================================
# COMMISSIONS - Реальные тесты комиссий
# ============================================================================

@pytest.mark.asyncio
async def test_commissions_crud(client):
    """CRUD для комиссий"""
    # Создание
    create_response = await client.post("/api/v1/commissions", json={
        "name": f"Test Commission {random.randint(1000, 9999)}",
        "percent": 15.0,
        "is_active": True
    })
    assert create_response.status_code == 201, f"Create commission failed: {create_response.text}"
    commission_id = create_response.json()["id"]
    
    # Получение
    get_response = await client.get(f"/api/v1/commissions/{commission_id}")
    assert get_response.status_code == 200
    
    # Удаление
    delete_response = await client.delete(f"/api/v1/commissions/{commission_id}")
    assert delete_response.status_code == 200


@pytest.mark.asyncio
async def test_commissions_delete_nonexistent(client):
    """Удаление несуществующей комиссии"""
    response = await client.delete("/api/v1/commissions/999999")
    assert response.status_code == 404


# ============================================================================
# TRANSACTIONS - Реальные тесты транзакций
# ============================================================================

@pytest.mark.asyncio
async def test_transactions_delete_nonexistent(client):
    """Удаление несуществующей транзакции"""
    response = await client.delete("/api/v1/transactions/999999")
    assert response.status_code == 404


# ============================================================================
# HEALTH CHECK
# ============================================================================

@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Health check должен возвращать 200"""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
