# Testing Strategy

> Страница вики. Уровень: подход к тестированию. Источник фактов — `tests/`,
> `pyproject.toml`, `reviews/test-coverage.md`.

## Конфигурация

`pyproject.toml`, `[tool.pytest.ini_options]`:

| Параметр | Значение | Где |
|---|---|---|
| `asyncio_mode` | `"auto"` | `pyproject.toml:56` |
| `pythonpath` | `["."]` | `pyproject.toml:57` |
| `testpaths` | `["tests"]` | `pyproject.toml:58` |
| `addopts` | `"-q"` | `pyproject.toml:59` |

Покрытие — `[tool.coverage]`: `branch = true`, `omit = ["alembic/*", "tests/*",
"litestar/*", "locustfile.py"]`, `fail_under = 100` (`pyproject.toml:61-67`).

## Уровни тестов и количество

Всего собрано **113 тестов** (`uv run pytest --collect-only` → «113 tests
collected in 0.16s», проверено 2026-09-03).

| Уровень | Файл | Тестов | Что покрывает |
|---|---|---|---|
| Unit | `tests/unit/test_value_objects.py` | 30 | `TargetUrl`, `ShortCode`, SSRF-фильтр |
| Unit | `tests/unit/test_link_service.py` | 19 | `LinkService` через `FakeLinkRepository` |
| Unit | `tests/unit/test_link_entity.py` | 11 | сущность `Link`, `LinkStatus`, поведение |
| Unit | `tests/unit/test_domain_errors.py` | 10 | доменные ошибки, сообщения, наследование |
| Unit | `tests/unit/test_api_errors.py` | 8 | маппинг ошибок в HTTP (`raise_for_domain_error`) |
| Unit | `tests/unit/test_api_deps.py` | 7 | `to_response` (DTO-маппер) |
| Integration | `tests/integration/test_links_api.py` | 14 | CRUD `/links` через httpx + реальная БД |
| Integration | `tests/integration/test_redirect.py` | 6 | редирект `GET /{short_code}` + статусы |

> Отчёт о покрытии 100% (строки и ветви) зафиксирован в `reviews/test-coverage.md`
> на коммите `bb6ba18` (дата 2025-09-02). Актуальный счётчик тестов — 113 (см. выше).

## Подход к изоляции

- **Unit-тесты сервиса** используют `FakeLinkRepository` — in-memory реализацию
  `LinkRepositoryProtocol` (`tests/unit/test_link_service.py:20-48`).
- **Без `unittest.mock`**: в `reviews/test-coverage.md` зафиксировано отсутствие
  `MagicMock`/`patch`/`unittest.mock`; используются только Fake-объекты.
- Фабрика `make_service()` (`tests/unit/test_link_service.py:51-54`) возвращает
  кортеж `(service, repo)`, что позволяет готовить состояние через публичный API
  Fake, не ломая инкапсуляцию. Это решение зафиксировано в
  `reviews/model-battle-unit.md` как сильная сторона выбранного варианта
  (`WINNER=workshop/unit-tests-glm`).

## Fixtures БД

- `tests/conftest.py:13-22` — `clean_db` (autouse): `DELETE FROM links` до и после
  каждого теста.
- `tests/integration/test_links_api.py:15-19` и `tests/integration/test_redirect.py:16-20`
  — собственные `clean_db` (autouse) с `DELETE FROM links` перед тестом.
- Integration-тесты ходят в приложение через `httpx.ASGITransport(app=app)` +
  `AsyncClient`, `follow_redirects=False` — `tests/integration/test_links_api.py:34-37`.
- `SessionLocal = get_sessionmaker()` — `tests/integration/test_links_api.py:12`,
  `tests/integration/test_redirect.py:13`.

## Coverage-гейт 100%

`fail_under = 100` в `pyproject.toml:67`. Отчёт `reviews/test-coverage.md`
подтверждает 100% по строкам и ветвям (318 stmts / 36 branches, 0 miss). В отчёте
также зафиксировано отсутствие запрещённых обходов покрытия:
`pytest.skip`, `xfail`, `pragma: no cover` — отсутствуют.

## Статические проверки

Из `reviews/test-coverage.md` и `reviews/orch-limit-ttl-seconds-max.md`:

- **ruff**: 0 errors.
- **basedpyright** (strict): 0 errors, 0 warnings.
- **bandit**: в конфиге `exclude_dirs = ["tests", "alembic"]`, `skips = ["B101"]`
  (`pyproject.toml:76-77`).

## Нагрузочное тестирование

`locustfile.py` — сценарий read-heavy. Константы:

- Веса задач запись:чтение:листинг = `3:6:1` (`_CREATE_WEIGHT=3`, `_GET_WEIGHT=6`,
  `_LIST_WEIGHT=1`) — `locustfile.py:20-22`.
- `wait_time = between(0.0, 0.05)` — `locustfile.py:38`.
- Кэш коротких кодов ограничен `_CODES_CACHE_LIMIT = 200` — `locustfile.py:14`,
  класс `LinkUser` (`locustfile.py:30`).

Появление locust-сценария и расширение пула — коммит `f1949f0 [agent]
perf(db): расширить пул соединений и добавить locust-сценарий`.

## Пробелы

- Integration-тесты требуют **реальную PostgreSQL** (нет in-memory БД для
  интеграций; `aiosqlite` есть в dev-зависимостях, но в `conftest.py`/тестах не
  используется — используется `get_sessionmaker()` от production-движка). См.
  [../decisions.md](../decisions.md).
- Нет отдельного теста на `resolve` несуществующего кода (покрыто косвенно через
  `test_get_link_nonexistent_raises`) — отмечено в `reviews/model-battle-unit.md`
  как слабое место.
