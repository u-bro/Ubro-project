## Тесты

- Предусловия: установлен Docker/Compose, Poetry. Все команды выполнять из каталога `Backend-Bot-master/Backend-Bot-master`.

- Установка зависимостей:
```bash
poetry install --no-interaction
```

- Прогон тестов (поднимается тестовый Postgres на 5443, применяются миграции):
```bash
poetry run pytest -q
```

- Генерация JUnit-отчёта:
```bash
mkdir -p scripts/reports
poetry run pytest -q --junitxml=scripts/reports/junit.xml
```

- Прогон отдельных файлов:
```bash
poetry run pytest tests_api_v1/test_health.py -vv
poetry run pytest tests_api_v1/test_users.py -vv
```

- Smoke-тест всех эндпоинтов по OpenAPI (нужен запущенный сервис):
```bash
poetry run python scripts/api_smoke_test.py http://localhost:8080
```

Примечания:
- Тестовая БД из `docker-compose-tests.yml` использует порт 5443 (локальные dev-контейнеры не мешают).
- Если нужно вручную остановить тестовую БД: `docker compose -f docker-compose-tests.yml down`.


