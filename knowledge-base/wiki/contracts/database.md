# Contract: Database

> Страница вики. Уровень: схема БД и маппинг. Источник фактов — `app/db/`,
> `app/repositories/`, `alembic/`.

## СУБД

PostgreSQL. Контейнер `postgres:17` — `docker-compose.yml`. Учётные данные по
умолчанию: `POSTGRES_USER=app`, `POSTGRES_PASSWORD=app`, `POSTGRES_DB=app`,
порт хоста `${POSTGRES_PORT:-5433}` → 5432 контейнера. Healthcheck
`pg_isready -U app -d app` — `docker-compose.yml:13`.

Строка подключения по умолчанию:
`postgresql+psycopg://app:app@localhost:5433/app` — `app/config.py:11`,
`.env.example:1`.

## Таблица `links`

### ORM-модель

`app/db/models.py:11-22`, класс `LinkModel` (`__tablename__ = "links"`).

| Колонка | Тип SQLAlchemy | Python | Ограничения | Где |
|---|---|---|---|---|
| `id` | `Integer` (primary) | `int` | PK | `:16` |
| `short_code` | `String(16)` | `str` | `unique=True`, `index=True` | `:17` |
| `target_url` | `String(2048)` | `str` | `nullable=False` | `:18` |
| `created_at` | `DateTime(timezone=True)` | `datetime` | `server_default=func.now()` | `:19` |
| `expires_at` | `DateTime(timezone=True)` | `datetime \| None` | `nullable=True` | `:20` |
| `clicks` | `Integer` | `int` | `default=0` | `:21` |
| `disabled` | `Boolean` | `bool` | `default=False` | `:22` |

### Миграция (первоначальная)

`alembic/versions/57054997f5e8_create_links_table.py`, revision `57054997f5e8`,
`down_revision = None`, Create Date `2026-08-31 21:44:32.941839`.

- `upgrade()` — `op.create_table("links", ...)` + `op.create_index(ix_links_short_code, unique=True)`.
- `downgrade()` — `op.drop_index(...)` + `op.drop_table("links")`.

> Внешний стандарт Alembic (цепочка `down_revision`, `NullPool` при миграциях) —
> см. [../../raw/alembic.md](../../raw/alembic.md).

### Базовый класс

`app/db/base.py:6`, `class Base(DeclarativeBase)` — база для всех ORM-моделей.
`target_metadata = Base.metadata` — `alembic/env.py:20`.

## Маппинг ORM ↔ домен

`app/repositories/link_repository.py:15-24`, функция `_to_domain`: собирает доменный
`Link` из `LinkModel` через конструкторы value objects `ShortCode(row.short_code)` и
`TargetUrl(row.target_url)`.

> Внимание: `_to_domain` пересоздаёт `TargetUrl`, что прогоняет SSRF/валидацию при
> каждом чтении из БД. Если в БД окажется невалидный URL (например, через прямой
> insert), `get_by_code` поднимет `InvalidUrlError`. Это побочный эффект
> «толстого» value object. См. [../decisions.md](../decisions.md).

## Репозиторий `LinkRepository`

`app/repositories/link_repository.py:27`, класс `LinkRepository(session)`.

| Метод | SQL-операция | Где | Тест |
|---|---|---|---|
| `add(link)` | `session.add(LinkModel)` + `flush` | `:33-44` | `test_post_link_saves_to_db` |
| `get_by_code(code)` | `select(...).where(short_code == code)` | `:46-49` | `test_get_link_by_code_returns_200` |
| `list_all(limit=100)` | `select order_by(id.desc()).limit(limit)` | `:51-54` | `test_list_links_returns_list` |
| `update(link)` | `update(...).where(short_code).values(clicks, disabled)` | `:56-64` | `test_redirect_increments_clicks`, `test_disable_link_updates_db` |
| `delete_by_code(code)` | `delete(...).where(short_code)` → `rowcount > 0` | `:66-72` | `test_delete_link_removes_from_db` |

Контракт репозитория зафиксирован как `typing.Protocol` `LinkRepositoryProtocol`
(`app/services/link_service.py:17-24`); реальный `LinkRepository` ему соответствует
(подтверждено отчётом `reviews/model-battle-unit.md`: «Fake соответствует реальному
`LinkRepositoryProtocol`»).

## Управление сессиями

`app/db/session.py`:

- `get_engine()` (`:17`) — lazy singleton `_engine`, `create_async_engine` с
  `pool_size`, `max_overflow`, `pool_pre_ping=True`.
- `get_sessionmaker()` (`:30`) — `async_sessionmaker(..., expire_on_commit=False)`.
- `provide_session()` (`:34`) — зависимость FastAPI: `yield session` → `commit`;
  при исключении → `rollback` + `raise`.

> Внешний стандарт SQLAlchemy (pool_pre_ping, expire_on_commit) —
> см. [../../raw/sqlalchemy.md](../../raw/sqlalchemy.md).

## Индексы

- `ix_links_short_code` — unique-индекс на `short_code` (`app/db/models.py:17`,
  миграция `57054997f5e8`). Обеспечивает уникальность кода на уровне БД и быстрый
  lookup для `get_by_code`.

## Пробелы

- Нет индекса на `expires_at`: при будущей очистке истёкших ссылок потребуется
  full scan. См. [../decisions.md](../decisions.md).
- `update()` не проверяет существование строки: `repository.update` выполняет
  UPDATE без проверки `rowcount` (`app/repositories/link_repository.py:56-64`);
  корректность гарантируется тем, что вызову `update` предшествует `get_link`
  (поднимающий `LinkNotFoundError`). См. [../decisions.md](../decisions.md).
