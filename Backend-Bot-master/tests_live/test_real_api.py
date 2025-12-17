"""
Реальные API тесты с проверкой бизнес-логики.
Синхронные тесты - работают без проблем с event loop.
"""
import pytest
import random


# ============================================================================
# USERS - Реальные тесты пользователей
# ============================================================================

def test_users_crud_full_cycle(client):
    """Полный цикл CRUD для пользователя"""
    telegram_id = random.randint(100000, 999999)
    
    # 1. Создание пользователя
    create_response = client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "TestCRUD",
        "username": f"testcrud_{telegram_id}"
    })
    assert create_response.status_code == 200, f"Create user failed: {create_response.text}"
    user_data = create_response.json()
    assert user_data["telegram_id"] == telegram_id
    user_id = user_data["id"]
    
    # 2. Повторный запрос - должен вернуть того же пользователя
    get_response = client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "Different",
        "username": f"different_{telegram_id}"
    })
    assert get_response.status_code == 200
    same_user = get_response.json()
    assert same_user["id"] == user_id
    
    # 3. Обновление пользователя
    update_response = client.put(f"/api/v1/users/{user_id}", json={
        "id": user_id,
        "telegram_id": telegram_id,
        "first_name": "UpdatedName",
        "username": f"updated_{telegram_id}",
        "balance": 100.0
    })
    assert update_response.status_code == 200
    
    # 4. Список пользователей
    list_response = client.get("/api/v1/users?page=1&page_size=100")
    assert list_response.status_code == 200
    assert isinstance(list_response.json(), list)


def test_users_update_nonexistent(client):
    """Обновление несуществующего пользователя"""
    response = client.put("/api/v1/users/999999", json={
        "id": 999999,
        "telegram_id": 999999,
        "first_name": "Ghost",
        "username": "ghost",
        "balance": 0.0
    })
    assert response.status_code in (404, 422)


# ============================================================================
# ROLES - Реальные тесты ролей  
# ============================================================================

def test_roles_crud_full_cycle(client):
    """Полный цикл CRUD для ролей"""
    role_code = f"test_role_{random.randint(10000, 99999)}"
    
    # 1. Создание роли
    create_response = client.post("/api/v1/roles", json={
        "code": role_code,
        "name": "Test Role",
        "description": "Role for testing"
    })
    assert create_response.status_code == 201
    role = create_response.json()
    role_id = role["id"]
    
    # 2. Получение по ID
    get_response = client.get(f"/api/v1/roles/{role_id}")
    assert get_response.status_code == 200
    
    # 3. Обновление
    update_response = client.put(f"/api/v1/roles/{role_id}", json={
        "name": "Updated Role Name"
    })
    assert update_response.status_code == 200
    
    # 4. Удаление
    delete_response = client.delete(f"/api/v1/roles/{role_id}")
    assert delete_response.status_code == 200
    
    # 5. Проверка что удалён
    get_after_delete = client.get(f"/api/v1/roles/{role_id}")
    assert get_after_delete.status_code == 404


def test_roles_delete_nonexistent(client):
    """Удаление несуществующей роли"""
    response = client.delete("/api/v1/roles/999999")
    assert response.status_code == 404


# ============================================================================
# RIDES - Реальные тесты поездок
# ============================================================================

def test_rides_create_and_get(client):
    """Создание и получение поездки"""
    telegram_id = random.randint(100000, 999999)
    user_response = client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "RideTestClient",
        "username": f"rideclient_{telegram_id}"
    })
    client_id = user_response.json()["id"]
    
    # Создаём поездку
    ride_response = client.post("/api/v1/rides", json={
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
    assert ride_response.status_code == 201
    ride = ride_response.json()
    ride_id = ride["id"]
    assert ride["status"] == "requested"
    
    # Получение по ID
    get_response = client.get(f"/api/v1/rides/{ride_id}")
    assert get_response.status_code == 200


def test_rides_change_status_not_found(client):
    """Смена статуса несуществующей поездки"""
    response = client.post("/api/v1/rides/999999/status", json={
        "to_status": "canceled",
        "reason": "Test",
        "actor_id": 1,
        "actor_role": "client"
    })
    assert response.status_code == 404


def test_rides_change_status_success(client):
    """Успешная смена статуса поездки"""
    telegram_id = random.randint(100000, 999999)
    user_response = client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "StatusTestClient",
        "username": f"statusclient_{telegram_id}"
    })
    client_id = user_response.json()["id"]
    
    ride_response = client.post("/api/v1/rides", json={
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
    
    # Меняем статус: requested -> canceled
    status_response = client.post(f"/api/v1/rides/{ride_id}/status", json={
        "to_status": "canceled",
        "reason": "Test cancellation",
        "actor_id": client_id,
        "actor_role": "client"
    })
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "canceled"


# ============================================================================
# DRIVER PROFILES - Реальные тесты профилей водителей
# ============================================================================

def test_driver_profile_create_success(client):
    """Создание профиля водителя"""
    telegram_id = random.randint(100000, 999999)
    user_response = client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "DriverProfileTest",
        "username": f"driverprofile_{telegram_id}"
    })
    user_id = user_response.json()["id"]
    
    # Создаём профиль водителя (согласно схеме - только user_id обязателен)
    profile_response = client.post("/api/v1/driver-profiles", json={
        "user_id": user_id,
        "first_name": "Driver",
        "last_name": "Test",
        "license_number": f"LIC{random.randint(100000, 999999)}"
    })
    assert profile_response.status_code == 201
    profile = profile_response.json()
    assert profile["user_id"] == user_id


def test_driver_profile_duplicate_user(client):
    """Повторное создание профиля для того же пользователя"""
    telegram_id = random.randint(100000, 999999)
    user_response = client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "DuplicateTest",
        "username": f"duplicate_{telegram_id}"
    })
    user_id = user_response.json()["id"]
    
    # Первый профиль - успешно
    first_profile = client.post("/api/v1/driver-profiles", json={
        "user_id": user_id,
        "first_name": "First"
    })
    assert first_profile.status_code == 201
    
    # Второй профиль для того же user_id - должен вернуть 409
    second_profile = client.post("/api/v1/driver-profiles", json={
        "user_id": user_id,
        "first_name": "Second"
    })
    assert second_profile.status_code == 409


# ============================================================================
# DRIVER LOCATIONS - Реальные тесты локаций водителей
# ============================================================================

def test_driver_location_foreign_key_error(client):
    """Создание локации с несуществующим driver_profile_id"""
    response = client.post("/api/v1/driver-locations", json={
        "driver_profile_id": 999999,
        "latitude": 50.45,
        "longitude": 30.52
    })
    assert response.status_code == 422


def test_driver_location_create_success(client):
    """Успешное создание локации водителя"""
    telegram_id = random.randint(100000, 999999)
    user_response = client.post(f"/api/v1/users/{telegram_id}", json={
        "telegram_id": telegram_id,
        "first_name": "LocationTest",
        "username": f"location_{telegram_id}"
    })
    user_id = user_response.json()["id"]
    
    profile_response = client.post("/api/v1/driver-profiles", json={
        "user_id": user_id
    })
    profile_id = profile_response.json()["id"]
    
    # Создаём локацию
    location_response = client.post("/api/v1/driver-locations", json={
        "driver_profile_id": profile_id,
        "latitude": 50.4501,
        "longitude": 30.5234
    })
    assert location_response.status_code == 201


# ============================================================================
# COMMISSIONS - Реальные тесты комиссий
# ============================================================================

def test_commissions_crud(client):
    """Полный цикл CRUD для комиссий"""
    create_response = client.post("/api/v1/commissions", json={
        "name": f"Test Commission {random.randint(1000, 9999)}",
        "percentage": 15.0
    })
    assert create_response.status_code == 201
    commission_id = create_response.json()["id"]
    
    # Получение
    get_response = client.get(f"/api/v1/commissions/{commission_id}")
    assert get_response.status_code == 200
    
    # Удаление
    delete_response = client.delete(f"/api/v1/commissions/{commission_id}")
    assert delete_response.status_code == 200


def test_commissions_delete_nonexistent(client):
    """Удаление несуществующей комиссии"""
    response = client.delete("/api/v1/commissions/999999")
    assert response.status_code == 404


# ============================================================================
# TRANSACTIONS - Реальные тесты транзакций
# ============================================================================

def test_transactions_delete_nonexistent(client):
    """Удаление несуществующей транзакции"""
    response = client.delete("/api/v1/transactions/999999")
    assert response.status_code == 404


# ============================================================================
# HEALTH - Проверка здоровья сервиса
# ============================================================================

def test_health_endpoint(client):
    """Health check"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
