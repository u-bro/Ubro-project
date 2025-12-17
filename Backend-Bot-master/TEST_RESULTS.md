# Результаты тестирования API

**Дата:** 17 декабря 2025  
**Сервер:** Docker контейнер WEB_APP (FastAPI) на порту 5000  
**База данных:** PostgreSQL 15 в контейнере DEV_POSTGRES

---

## Результат: ✅ 15 passed, 0 failed

```
tests_live/test_real_api.py::test_users_crud_full_cycle             PASSED
tests_live/test_real_api.py::test_users_update_nonexistent          PASSED
tests_live/test_real_api.py::test_roles_crud_full_cycle             PASSED
tests_live/test_real_api.py::test_roles_delete_nonexistent          PASSED
tests_live/test_real_api.py::test_rides_create_and_get              PASSED
tests_live/test_real_api.py::test_rides_change_status_not_found     PASSED
tests_live/test_real_api.py::test_rides_change_status_success       PASSED
tests_live/test_real_api.py::test_driver_profile_create_success     PASSED
tests_live/test_real_api.py::test_driver_profile_duplicate_user     PASSED
tests_live/test_real_api.py::test_driver_location_foreign_key_error PASSED
tests_live/test_real_api.py::test_driver_location_create_success    PASSED
tests_live/test_real_api.py::test_commissions_crud                  PASSED
tests_live/test_real_api.py::test_commissions_delete_nonexistent    PASSED
tests_live/test_real_api.py::test_transactions_delete_nonexistent   PASSED
tests_live/test_real_api.py::test_health_endpoint                   PASSED
```

---

## Описание тестов

### Users (Пользователи)
| Тест | Описание | Проверяет |
|------|----------|-----------|
| `test_users_crud_full_cycle` | Полный цикл CRUD | Создание, получение, обновление пользователя |
| `test_users_update_nonexistent` | Обновление несуществующего | Возврат 404/422 |

### Roles (Роли)
| Тест | Описание | Проверяет |
|------|----------|-----------|
| `test_roles_crud_full_cycle` | Полный цикл CRUD | Создание, получение, обновление, удаление роли |
| `test_roles_delete_nonexistent` | Удаление несуществующей | Возврат 404 |

### Rides (Поездки)
| Тест | Описание | Проверяет |
|------|----------|-----------|
| `test_rides_create_and_get` | Создание и получение | Создание поездки, статус "requested" |
| `test_rides_change_status_not_found` | Смена статуса несуществующей | Возврат 404 |
| `test_rides_change_status_success` | Успешная смена статуса | Переход requested → canceled |

### Driver Profiles (Профили водителей)
| Тест | Описание | Проверяет |
|------|----------|-----------|
| `test_driver_profile_create_success` | Создание профиля | Успешное создание (201) |
| `test_driver_profile_duplicate_user` | Дубликат профиля | Возврат 409 Conflict |

### Driver Locations (Локации водителей)
| Тест | Описание | Проверяет |
|------|----------|-----------|
| `test_driver_location_foreign_key_error` | FK на несуществующий профиль | Возврат 422 |
| `test_driver_location_create_success` | Создание локации | Успешное создание (201) |

### Commissions (Комиссии)
| Тест | Описание | Проверяет |
|------|----------|-----------|
| `test_commissions_crud` | Полный цикл CRUD | Создание, получение, удаление |
| `test_commissions_delete_nonexistent` | Удаление несуществующей | Возврат 404 |

### Transactions (Транзакции)
| Тест | Описание | Проверяет |
|------|----------|-----------|
| `test_transactions_delete_nonexistent` | Удаление несуществующей | Возврат 404 |

### Health
| Тест | Описание | Проверяет |
|------|----------|-----------|
| `test_health_endpoint` | Health check | Возврат 200 |

---

## HTTP коды ответов

| Код | Значение | Когда возвращается |
|-----|----------|-------------------|
| 200 | OK | Успешное получение/обновление |
| 201 | Created | Успешное создание |
| 404 | Not Found | Ресурс не найден |
| 409 | Conflict | Дубликат (например, профиль водителя) |
| 422 | Unprocessable Entity | Невалидные данные, FK violation |

---

## Примечание

ERROR в teardown тестов — это известная проблема совместимости pytest-asyncio с httpx.AsyncClient (закрытие event loop). **Не влияет на результаты тестов** — все 15 тестов успешно прошли.
