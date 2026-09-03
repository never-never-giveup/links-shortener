# Architecture

> Страница вики. Уровень: слои приложения и поток запроса. Источник фактов — код.

## Слоистая архитектура

Приложение разделено на слои. Зависимости направлены внутрь (домен не зависит от
транспорта и БД).

```
HTTP (FastAPI routes)  →  services (бизнес-логика)  →  domain (сущности/VO)
        │                         │
        └── api/schemas, deps     └── repositories ──→ db (ORM-модели, сессия)
```

### Слой `app/api/` — транспорт (HTTP)

| Файл | Назначение | Ключевые имена |
|---|---|---|
| `app/main.py` | Создание приложения FastAPI, маршрут редиректа | `create_app`, `redirect_to_target`, `app` |
| `app/api/routes.py` | CRUD-маршруты `/links` | `router`, `create_link`, `list_links`, `get_link`, `disable_link`, `delete_link` |
| `app/api/schemas.py` | Pydantic DTO запросов/ответов | `CreateLinkRequest`, `LinkResponse`, `MAX_TTL_SECONDS` |
| `app/api/deps.py` | DI: сессия БД, сервис, маппер в ответ | `SessionDep`, `ServiceDep`, `get_link_service`, `to_response` |
| `app/api/errors.py` | Маппинг доменных ошибок в HTTP | `raise_for_domain_error`, `_STATUS_BY_ERROR` |

### Слой `app/services/` — бизнес-логика

| Файл | Назначение | Ключевые имена |
|---|---|---|
| `app/services/link_service.py` | Операции над ссылками | `LinkService`, `LinkRepositoryProtocol` |

`LinkService` зависит от `LinkRepositoryProtocol` (typing.Protocol), что позволяет
подменять реализацию в unit-тестах — `app/services/link_service.py:17-24`.

### Слой `app/domain/` — домен (без I/O)

| Файл | Назначение | Ключевые имена |
|---|---|---|
| `app/domain/link.py` | Сущность `Link`, её статус и поведение | `Link`, `LinkStatus` |
| `app/domain/value_objects.py` | `TargetUrl`, `ShortCode` + инварианты/SSRF-фильтр | `TargetUrl`, `ShortCode`, `_reject_ssrf` |
| `app/domain/codegen.py` | Генерация случайного кода | `generate_short_code` |
| `app/domain/errors.py` | Доменные ошибки | `DomainError` и наследники |

Доменные сущности и value objects — `@dataclass(frozen=True, slots=True)`
(неизменяемые): `app/domain/link.py:17`, `app/domain/value_objects.py:41,64`.

### Слой `app/repositories/` — доступ к данным

| Файл | Назначение | Ключевые имена |
|---|---|---|
| `app/repositories/link_repository.py` | Доступ к таблице `links`, маппинг ORM↔домен | `LinkRepository`, `_to_domain` |

Репозиторий принимает и возвращает доменные объекты, скрывая ORM —
`app/repositories/link_repository.py:27`.

### Слой `app/db/` — инфраструктура БД

| Файл | Назначение | Ключевые имена |
|---|---|---|
| `app/db/base.py` | Базовый класс ORM-моделей | `Base` |
| `app/db/models.py` | ORM-модель таблицы `links` | `LinkModel` |
| `app/db/session.py` | Engine, sessionmaker, зависимость сессии | `get_engine`, `get_sessionmaker`, `provide_session` |

### Слой `app/config.py` — конфигурация

`Settings(BaseSettings)` читает переменные окружения и `.env` —
`app/config.py:6-18`. `get_settings()` — фабрика настроек — `app/config.py:21`.

## Поток запроса `POST /links`

1. FastAPI валидирует тело через `CreateLinkRequest` (`app/api/schemas.py:10`).
2. Маршрут `create_link` (`app/api/routes.py:13`) вызывает `service.create_link(...)`.
3. `LinkService.create_link` (`app/services/link_service.py:38`):
   - если задан `custom_code` — проверяет занятость через `repository.get_by_code`,
     при совпадении поднимает `ShortCodeTakenError`;
   - иначе генерирует код `generate_short_code` (`app/domain/codegen.py:8`);
   - считает `expires_at` из `ttl_seconds`;
   - строит доменный `Link` и вызывает `repository.add`.
4. `LinkRepository.add` (`app/repositories/link_repository.py:33`) flush'ит ORM-строку,
   возвращает доменный объект с присвоенным `id`.
5. Маршрут вызывает `to_response(link)` (`app/api/deps.py:26`) → `LinkResponse`.
6. `provide_session` коммитит транзакцию (`app/db/session.py:38-39`).
7. При `DomainError` — `raise_for_domain_error` маппит в HTTP-код
   (`app/api/errors.py:27`).

## Поток запроса `GET /{short_code}` (редирект)

1. Маршрут `redirect_to_target` (`app/main.py:12`) вызывает `service.resolve`.
2. `LinkService.resolve` (`app/services/link_service.py:71`):
   - `get_link` → при `None` поднимает `LinkNotFoundError`;
   - вычисляет `link.status(now)`; для `EXPIRED` → `LinkExpiredError`, для
     `DISABLED` → `LinkDisabledError`;
   - для активной — `repository.update(link.with_click())` (инкремент `clicks`).
3. Возвращает `RedirectResponse(url=target_url, status_code=307)` —
   `app/main.py:17-18`.

## Конфигурация запуска

| Параметр | Значение по умолчанию | Где |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://app:app@localhost:5433/app` | `app/config.py:11` |
| `BASE_URL` | `http://127.0.0.1:8000` | `app/config.py:12` |
| `CODE_LENGTH` | `7` | `app/config.py:13` |
| `POOL_SIZE` | `20` | `app/config.py:16` |
| `MAX_OVERFLOW` | `10` | `app/config.py:18` |

Комментарии в `app/config.py:14-18` объясняют выбор `pool_size=20`: при `pool_size=5`
запросы ждут свободный коннект, раздувая p95 чтения (~380ms на 100 users). Это
согласуется с историей git — коммит `f1949f0 [agent] perf(db): расширить пул
соединений`.

## Связанные страницы

- [overview.md](overview.md) — общий обзор.
- [domain/links.md](domain/links.md) — доменные правила.
- [contracts/http-api.md](contracts/http-api.md) — HTTP-контракт.
- [contracts/database.md](contracts/database.md) — схема БД.
- [decisions.md](decisions.md) — решения по пулу соединений и др.

## Пробелы

- Структурированное логирование через `structlog` объявлено зависимостью
  (`pyproject.toml`), но в коде приложения (`app/`) **нет вызовов structlog**.
  Инструкции по логированию есть во внутреннем правиле `.agents/agents/logging.md`,
  но в приложении не реализованы. См. [decisions.md](decisions.md).
