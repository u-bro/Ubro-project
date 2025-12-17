# Инструкция по запуску

## Требования

- Docker и Docker Compose
- Python 3.12+ (для запуска тестов локально)
- WSL2 (для Windows)

---

## Быстрый старт

### 1. Запуск сервиса

```bash
cd Backend-Bot-master
docker compose up -d --build
```

Это запустит:
- **WEB_APP** — FastAPI сервер на порту 5000
- **DEV_POSTGRES** — PostgreSQL 15 на порту 5432
- **PUBLIC_TUNNEL** — Cloudflare туннель (опционально)

### 2. Применение миграций (обязательно при первом запуске!)

```bash
# Войти в контейнер приложения
docker exec -it WEB_APP bash

# Применить все миграции
alembic upgrade head

# Выйти из контейнера
exit
```

Или одной командой:
```bash
docker exec -it WEB_APP alembic upgrade head
```

### 3. Проверка работы

```bash
# Проверить что контейнеры запущены
docker ps

# Проверить health endpoint
curl http://localhost:5000/api/v1/health

# Открыть Swagger UI в браузере
# http://localhost:5000/docs
```

### 4. Просмотр логов

```bash
# Логи приложения
docker logs WEB_APP -f

# Логи базы данных
docker logs DEV_POSTGRES -f
```

---

## Работа с миграциями

### Создание новой миграции

```bash
# Автогенерация на основе изменений в моделях
docker exec -it WEB_APP alembic revision --autogenerate -m "описание изменений"
```

### Применение миграций

```bash
# Применить все новые миграции
docker exec -it WEB_APP alembic upgrade head

# Откатить последнюю миграцию
docker exec -it WEB_APP alembic downgrade -1

# Посмотреть текущую версию
docker exec -it WEB_APP alembic current

# Посмотреть историю миграций
docker exec -it WEB_APP alembic history
```

---

## Запуск тестов

### Установка зависимостей (один раз)

```bash
pip install pytest pytest-asyncio httpx
```

### Запуск реальных тестов

```bash
# 1. Убедитесь что сервис запущен
docker compose up -d

# 2. Убедитесь что миграции применены
docker exec -it WEB_APP alembic upgrade head

# 3. Запуск тестов
pytest tests_live/test_real_api.py -v
```

### Ожидаемый результат

```
15 passed, 0 failed
```

---

## Структура проекта

```
Backend-Bot-master/
├── app/
│   ├── backend/
│   │   ├── main.py           # Точка входа FastAPI
│   │   ├── routers/          # API эндпоинты
│   │   └── middlewares/      # Middleware (DB, исключения)
│   ├── crud/                 # Операции с БД
│   ├── models/               # SQLAlchemy модели
│   └── schemas/              # Pydantic схемы
├── migrations/               # Alembic миграции
├── tests_live/               # Интеграционные тесты
│   ├── conftest.py           # Фикстуры pytest
│   ├── test_real_api.py      # Реальные API тесты
│   └── test_full_swagger.py  # Тесты всех эндпоинтов
├── docker-compose.yml        # Docker конфигурация
├── Dockerfile                # Образ приложения
└── pyproject.toml            # Зависимости Python
```

---

## API эндпоинты

Base URL: `http://localhost:5000/api/v1`

### Users (Пользователи)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/users` | Список пользователей (пагинация) |
| POST | `/users/{telegram_id}` | Создать или получить пользователя |
| PUT | `/users/{id}` | Обновить пользователя |
| PATCH | `/users/update_user_balance/{user_id}` | Обновить баланс |

### Rides (Поездки)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/rides` | Список поездок (пагинация) |
| GET | `/rides/count` | Количество поездок |
| GET | `/rides/{ride_id}` | Получить поездку по ID |
| POST | `/rides` | Создать поездку |
| PUT | `/rides/{ride_id}` | Обновить поездку |
| POST | `/rides/{ride_id}/status` | Изменить статус поездки |

### Roles (Роли)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/roles` | Список ролей (пагинация) |
| GET | `/roles/count` | Количество ролей |
| GET | `/roles/{item_id}` | Получить роль по ID |
| POST | `/roles` | Создать роль |
| PUT | `/roles/{item_id}` | Обновить роль |
| DELETE | `/roles/{item_id}` | Удалить роль |

### Driver Profiles (Профили водителей)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/driver-profiles` | Список профилей (пагинация) |
| GET | `/driver-profiles/count` | Количество профилей |
| GET | `/driver-profiles/{item_id}` | Получить профиль по ID |
| POST | `/driver-profiles` | Создать профиль |
| PUT | `/driver-profiles/{item_id}` | Обновить профиль |
| DELETE | `/driver-profiles/{item_id}` | Удалить профиль |

### Driver Locations (Локации водителей)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/driver-locations` | Список локаций (пагинация) |
| GET | `/driver-locations/count` | Количество локаций |
| GET | `/driver-locations/{item_id}` | Получить локацию по ID |
| POST | `/driver-locations` | Создать локацию |
| PUT | `/driver-locations/{item_id}` | Обновить локацию |
| DELETE | `/driver-locations/{item_id}` | Удалить локацию |

### Driver Documents (Документы водителей)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/driver-documents` | Список документов (пагинация) |
| GET | `/driver-documents/count` | Количество документов |
| GET | `/driver-documents/{item_id}` | Получить документ по ID |
| POST | `/driver-documents` | Создать документ |
| PUT | `/driver-documents/{item_id}` | Обновить документ |
| DELETE | `/driver-documents/{item_id}` | Удалить документ |

### Commissions (Комиссии)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/commissions` | Список комиссий (пагинация) |
| GET | `/commissions/count` | Количество комиссий |
| GET | `/commissions/{item_id}` | Получить комиссию по ID |
| POST | `/commissions` | Создать комиссию |
| PUT | `/commissions/{item_id}` | Обновить комиссию |
| DELETE | `/commissions/{item_id}` | Удалить комиссию |

### Transactions (Транзакции)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/transactions` | Список транзакций (пагинация) |
| GET | `/transactions/count` | Количество транзакций |
| GET | `/transactions/{item_id}` | Получить транзакцию по ID |
| POST | `/transactions` | Создать транзакцию |
| PUT | `/transactions/{item_id}` | Обновить транзакцию |
| DELETE | `/transactions/{item_id}` | Удалить транзакцию |

### Chat Messages (Сообщения чата)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/chat-messages` | Список сообщений (пагинация) |
| GET | `/chat-messages/count` | Количество сообщений |
| GET | `/chat-messages/{item_id}` | Получить сообщение по ID |
| POST | `/chat-messages` | Создать сообщение |
| PUT | `/chat-messages/{item_id}` | Обновить сообщение |
| DELETE | `/chat-messages/{item_id}` | Удалить сообщение |

### Phone Verifications (Верификация телефонов)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/phone-verifications` | Список верификаций (пагинация) |
| GET | `/phone-verifications/count` | Количество верификаций |
| GET | `/phone-verifications/{item_id}` | Получить верификацию по ID |
| POST | `/phone-verifications` | Создать верификацию |
| PUT | `/phone-verifications/{item_id}` | Обновить верификацию |
| DELETE | `/phone-verifications/{item_id}` | Удалить верификацию |

### Health
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Health check |

Полная документация: http://localhost:5000/docs

---

## Переменные окружения

Файл `.env` (создаётся автоматически или вручную):

```env
# База данных
POSTGRES_USER=test
POSTGRES_PASSWORD=test
POSTGRES_DB=test
POSTGRES_HOST=DEV_POSTGRES
POSTGRES_PORT=5432

# Приложение
DEBUG=true
```

---

## Остановка сервиса

```bash
docker compose down
```

Для полной очистки (включая volumes):

```bash
docker compose down -v
```

---

## Решение проблем

### Контейнер не запускается

```bash
# Посмотреть логи
docker logs WEB_APP

# Пересобрать с нуля
docker compose down -v
docker compose up -d --build
```

### Ошибка подключения к БД

```bash
# Проверить что postgres работает
docker logs DEV_POSTGRES

# Проверить порт
docker port DEV_POSTGRES
```

### Тесты не проходят

1. Убедитесь что сервис запущен: `docker ps`
2. Проверьте доступность: `curl http://localhost:5000/api/v1/health`
3. Посмотрите логи: `docker logs WEB_APP`
