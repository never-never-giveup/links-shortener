# Runbook: Local Development

> Страница вики. Уровень: инструкция запуска. Источник фактов — `docker-compose.yml`,
> `pyproject.toml`, `.env.example`, `.pre-commit-config.yaml`, `alembic.ini`.

## Предварительные требования

- Python **>=3.14** (`pyproject.toml`, `requires-python`).
- Менеджер зависимостей **uv** (pre-commit использует `uv run ...` —
  `.pre-commit-config.yaml:26,31,38,44,50`).
- Docker (для PostgreSQL) — `docker-compose.yml`.

## 1. База данных

```bash
docker compose up -d db
```

Поднимает `postgres:17` на порту `${POSTGRES_PORT:-5433}` → 5432, с volume
`pgdata` и healthcheck `pg_isready` — `docker-compose.yml:1-19`.

## 2. Конфигурация окружения

Скопировать `.env.example` → `.env` (`.env` в `.gitignore:4`). Параметры:

| Переменная | Значение по умолчанию | Где |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://app:app@localhost:5433/app` | `.env.example:1`, `app/config.py:11` |
| `BASE_URL` | `http://127.0.0.1:8000` | `.env.example:2`, `app/config.py:12` |
| `CODE_LENGTH` | `7` | `.env.example:3`, `app/config.py:13` |
| `POOL_SIZE` | `20` | `.env.example:4`, `app/config.py:16` |
| `MAX_OVERFLOW` | `10` | `.env.example:5`, `app/config.py:18` |

`Settings` читает `.env` (`env_file=".env"`, `env_file_encoding="utf-8"`,
`extra="ignore"`) — `app/config.py:9`.

## 3. Установка зависимостей

```bash
uv sync
```

(dev-зависимости — в группе `[dependency-groups] dev`, `pyproject.toml:15-28`).

## 4. Миграции схемы

```bash
uv run alembic upgrade head
```

Конфигурация `alembic.ini` (`script_location = alembic`, `prepend_sys_path = .`).
Асинхронный прогон — `alembic/env.py:29-44` (`run_async_migrations` использует
`async_engine_from_config` с `NullPool`). Единственная миграция —
`57054997f5e8_create_links_table`.

## 5. Запуск приложения

```bash
uv run fastapi dev
```

> Пробел: явная команда запуска не задокументирована в `README.md` (его нет в
> репозитории). Команда выведена из стандартного поведения FastAPI
> ([../../raw/fastapi.md](../../raw/fastapi.md)) и наличия точки входа `app.main:app`
> (`app/main.py:29`). Базовый URL по умолчанию — `http://127.0.0.1:8000`.

## 6. Проверки (lint/type/test)

```bash
uv run ruff check .
uv run basedpyright
uv run pytest -q
```

Это три обязательные проверки из `.agents/AGENTS.md` (правило 5). Покрытие:

```bash
uv run pytest --cov=app --cov-branch --cov-report=term-missing --cov-fail-under=100
```

(команда из `reviews/test-coverage.md`). Ожидаемый результат: 113 passed, 100%
покрытия — см. [../testing/strategy.md](../testing/strategy.md).

## 7. Нагрузочное тестирование

```bash
uv run locust -f locustfile.py
```

Сценарий read-heavy (веса 3:6:1) — `locustfile.py`. По умолчанию locust поднимает
веб-UI на `http://localhost:8089`.

## 8. Pre-commit хуки

`.pre-commit-config.yaml` (Python 3.14):

| Хук | Назначение |
|---|---|
| `check-added-large-files`, `check-case-conflict`, `check-merge-conflict`, `check-toml`, `check-yaml`, `debug-statements`, `end-of-file-fixer`, `trailing-whitespace` | базовые проверки |
| `gitleaks` (v8.21.2) | поиск секретов |
| `ruff-check` (`uv run ruff check --fix --force-exclude`) | линтер + автофикс |
| `ruff-format` (`uv run ruff format --force-exclude`) | форматирование |
| `basedpyright` (без передачи файлов) | типы (strict) |
| `bandit` (`-r app tests`) | безопасность |
| `pip-audit` | CVE в зависимостях |
| `uv-lock-check` (`uv lock --check`) | консистентность lock-файла |

> Запрещено обходить хуки (`--no-verify`, `SKIP=...`) — `.agents/AGENTS.md`,
> раздел «Что запрещено делать».

## Пробелы

- Нет `README.md` с разделом Quickstart — запуск reconstructed из конфигурации,
  а не из документации. См. [../decisions.md](../decisions.md).
- Нет CI-конфигурации для приложения (файл `.gitlab-ci.yml` есть только в
  `.agents/` и относится к репозиторию правил). См. [../decisions.md](../decisions.md).
