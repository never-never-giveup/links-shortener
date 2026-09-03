# Decisions

> Страница вики. Уровень: зафиксированные решения, их обоснования и пробелы.
> Источник фактов — код, git-история, `reviews/`, правила `.agents/`.

## Зафиксированные решения

### D1. Верхняя граница TTL = 86400 секунд (сутки)

- **Что:** в `POST /links` поле `ttl_seconds` ограничено сверху `MAX_TTL_SECONDS = 86_400`.
  При превышении Pydantic отдаёт 422.
- **Где:** `app/api/schemas.py:7` (`MAX_TTL_SECONDS`), `app/api/schemas.py:12`
  (`Field(default=None, gt=0, le=MAX_TTL_SECONDS)`).
- **Тесты:** `test_post_link_ttl_max_returns_201` (86400 → 201),
  `test_post_link_ttl_over_max_returns_422` (86401 → 422, БД пуста) —
  `tests/integration/test_links_api.py`.
- **История:** коммит `815c70c [agent] feat(links): ограничить ttl_seconds сверху
  максимумом 86400 (сутки), 422 при превышении`; смёржен в `f7d5467` (PR #4).
- **Артефакт оркестрации:** `reviews/orch-limit-ttl-seconds-max.md` (Coder:
  deepseek-v4-pro, Reviewer: kimi-k2.7-code, verdict `MERGE`, claim ledger с
  GROUNDED-утверждениями).

### D2. Размер пула соединений БД = 20 (+ max_overflow 10)

- **Что:** `pool_size=20`, `max_overflow=10`, `pool_pre_ping=True`.
- **Где:** `app/config.py:16-18`, `app/db/session.py:21-26` (`get_engine`).
- **Обоснование в коде:** комментарий `app/config.py:14-15` — при `pool_size=5`
  запросы ждут свободный коннект, раздувая p95 чтения (~380ms на 100 users).
- **История:** коммит `f1949f0 [agent] perf(db): расширить пул соединений и
  добавить locust-сценарий`.

### D3. Read-heavy профиль нагрузки (веса 3:6:1)

- **Что:** locust-сценарий: создание 3, чтение 6, листинг 1.
- **Где:** `locustfile.py:20-22` (`_CREATE_WEIGHT`, `_GET_WEIGHT`, `_LIST_WEIGHT`),
  класс `LinkUser` (`locustfile.py:30`).
- **Обоснование в коде:** комментарий `locustfile.py:18-19` — «Чтение доминирует,
  как в реальном трафике сокращателя ссылок».
- **История:** коммит `f1949f0`.

### D4. Неизменяемый домен (frozen dataclasses)

- **Что:** `Link`, `TargetUrl`, `ShortCode` — `@dataclass(frozen=True, slots=True)`;
  модификация через `replace`/копирование (`with_click`, `disable`).
- **Где:** `app/domain/link.py:17`, `app/domain/value_objects.py:41,64`,
  `app/domain/link.py:40,44`.
- **Следствие:** `repository.update` переписывает `clicks`/`disabled` целиком по
  `short_code`, а не инкрементирует на месте —
  `app/repositories/link_repository.py:56-64`.

### D5. Репозиторий через Protocol для тестируемости

- **Что:** `LinkService` зависит от `LinkRepositoryProtocol` (typing.Protocol), а не
  от конкретного `LinkRepository`. В unit-тестах подменяется `FakeLinkRepository`.
- **Где:** `app/services/link_service.py:17-24,30-36`, `tests/unit/test_link_service.py:20-54`.
- **Обоснование:** зафиксировано в `reviews/model-battle-unit.md` — выбран вариант,
  где Fake полностью повторяет async-контракт репозитория; проигравший вариант
  нарушал type safety (доступ к `service._repository._store` через `# type: ignore`).

### D6. SSRF-фильтр на этапе создания (статический, без DNS)

- **Что:** `TargetUrl` блокирует loopback/private/reserved/multicast/unspecified IP
  и имена `localhost`/`ip6-localhost` при конструировании.
- **Где:** `app/domain/value_objects.py:21-38` (`_reject_ssrf`), вызывается из
  `TargetUrl.__post_init__` (`:60`).
- **Ограничение:** фильтр статический — не делает DNS-резолв, поэтому домен,
  резолвящийся в приватный IP, не блокируется. Это явно отмечено в docstring
  функции (`app/domain/value_objects.py:22`): «Блокирует очевидные SSRF-цели на
  этапе создания (статически, без DNS)».
- **Тесты:** `test_targeturl_*_raises` — `tests/unit/test_value_objects.py`.

### D7. Маппинг доменных ошибок в HTTP через словарь

- **Что:** `_STATUS_BY_ERROR: dict[type[DomainError], int]` + `raise_for_domain_error`.
  Неизвестный наследник `DomainError` → 500.
- **Где:** `app/api/errors.py:17-30`.
- **Тесты:** `test_raise_for_unknown_domain_error_returns_500`,
  `test_raise_for_domain_error_preserves_cause` — `tests/unit/test_api_errors.py`.

### D8. Триггер редиректа — 307

- **Что:** `GET /{short_code}` возвращает `307 Temporary Redirect`.
- **Где:** `app/main.py:17-18` (`RedirectResponse(..., status_code=HTTP_307_TEMPORARY_REDIRECT)`).
- **Тест:** `test_redirect_active_link_returns_307` (`tests/integration/test_redirect.py:36`).

## Пробелы

Пробел = факт, который не удалось подтвердить кодом/тестом/документацией. Не
додумывается.

### G1. Отсутствует `README.md`

Правила `.agents/agents/docs.md` (раздел «README.md») требуют разделы Overview,
Quickstart, Configuration, Running, Architecture, API. В корне репозитория файла
нет (`git ls-files` — подтверждено 2026-09-03).

### G2. Отсутствует `CHANGELOG.md`

Правила `.agents/agents/docs.md` (раздел «CHANGELOG.md») предписывают Keep a
Changelog с секцией `[Unreleased]`. В корне репозитория файла нет
([../raw/keep-a-changelog.md](../raw/keep-a-changelog.md)).

### G3. Нет CI для приложения

Файл `.gitlab-ci.yml` существует только в `.agents/` и содержит комментарий:
«Минимальный CI для документационного репозитория» (`.agents/.gitlab-ci.yml:1`).
Для FastAPI-приложения CI-конфигурации нет.

### G4. structlog объявлен, но не используется

`structlog>=24.4.0` — зависимость (`pyproject.toml:12`), но вызовов `structlog`
в коде приложения (`app/`) нет. Правила логирования описаны во внутреннем файле
`.agents/agents/logging.md`, но в приложении не реализованы.

### G5. Нет retry при коллизии сгенерированного кода

`LinkService.create_link` при автоматической генерации не проверяет, что код
свободен — `app/services/link_service.py:49-50`. Уникальность гарантирует
DB-constraint (`ix_links_short_code`), но при коллизии возникнет ошибка БД, а не
доменная. Поведение при коллизии не покрыто тестом.

### G6. `repository.update` без проверки существования

`LinkRepository.update` выполняет UPDATE без проверки `rowcount`
(`app/repositories/link_repository.py:56-64`). Корректность обеспечивается слоем
выше (`resolve`/`disable_link` сначала делают `get_link`), но инвариант не
формализован в коде репозитория.

### G7. Нет индекса на `expires_at`

При будущей задаче очистки истёкших ссылок потребуется full scan таблицы `links`.
Индекса на `expires_at` нет (`app/db/models.py:11-22`, миграция `57054997f5e8`).

### G8. Integration-тесты требуют реальную PostgreSQL

`aiosqlite` есть в dev-зависимостях (`pyproject.toml:21`), но в `conftest.py` и
integration-тестах используется production-движок (`get_sessionmaker()`). Запуск
тестов невозможен без запущенной PostgreSQL.

## Связанные страницы

- [overview.md](overview.md) — сводка пробелов.
- [architecture.md](architecture.md) — слои.
- [domain/links.md](domain/links.md) — доменные правила.
- [contracts/database.md](contracts/database.md) — G6, G7.
- [testing/strategy.md](testing/strategy.md) — G8.
