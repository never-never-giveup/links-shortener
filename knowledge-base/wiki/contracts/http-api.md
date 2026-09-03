# Contract: HTTP API

> Страница вики. Уровень: внешний HTTP-контракт. Источник фактов — `app/api/`.

## Базовый путь

- CRUD-маршруты вынесены в роутер `APIRouter(prefix="/links", tags=["links"])` —
  `app/api/routes.py:10`.
- Маршрут редиректа `GET /{short_code}` регистрируется отдельно на приложении —
  `app/main.py:25`.
- Приложение: `FastAPI(title="Link Shortener (FastAPI track)")` —
  `app/main.py:23`.

## Эндпоинты

### `POST /links` — создать ссылку

- Файл:функция: `app/api/routes.py:13` `create_link`.
- Успех: `201 Created`, тело `LinkResponse`.
- Тело запроса — `CreateLinkRequest` (`app/api/schemas.py:10`):

| Поле | Тип | Ограничение | Где |
|---|---|---|---|
| `url` | `str` | обязательное | `app/api/schemas.py:11` |
| `ttl_seconds` | `int \| None` | `default=None`, `gt=0`, `le=MAX_TTL_SECONDS` (86400) | `app/api/schemas.py:12` |
| `custom_code` | `str \| None` | `default=None` | `app/api/schemas.py:13` |

- `MAX_TTL_SECONDS = 86_400` — `app/api/schemas.py:7`.
- Валидация URL/кода и TTL-логика — в домене (см. [../domain/links.md](../domain/links.md)).
- Тесты: `test_post_link_returns_201`, `test_post_link_with_custom_code`,
  `test_post_link_empty_url_returns_422`, `test_post_link_invalid_url_returns_422`,
  `test_post_link_duplicate_custom_code_returns_409`, `test_post_link_with_ttl_returns_expires`,
  `test_post_link_negative_ttl_returns_422`, `test_post_link_ttl_max_returns_201`,
  `test_post_link_ttl_over_max_returns_422`, `test_post_link_ttl_one_returns_201_with_expires`,
  `test_post_link_without_ttl_returns_201_no_expires` — `tests/integration/test_links_api.py`.

### `GET /links` — список ссылок

- Файл:функция: `app/api/routes.py:24` `list_links`.
- Успех: `200 OK`, тело `list[LinkResponse]`.
- Лимит по умолчанию 100 — `LinkService.list_links` (`app/services/link_service.py:68`).
- Тесты: `test_list_links_returns_list`, `test_list_links_empty_returns_empty_list`.

### `GET /links/{short_code}` — получить ссылку

- Файл:функция: `app/api/routes.py:30` `get_link`.
- Успех: `200 OK`, тело `LinkResponse`.
- Тесты: `test_get_link_by_code_returns_200`, `test_get_link_nonexistent_returns_404`.

### `POST /links/{short_code}/disable` — отключить ссылку

- Файл:функция: `app/api/routes.py:39` `disable_link`.
- Успех: `200 OK`, тело `LinkResponse` (с `disabled=True`).
- Тесты: `test_disable_link_returns_200`, `test_disable_link_nonexistent_returns_404`,
  `test_disable_link_updates_db`.

### `DELETE /links/{short_code}` — удалить ссылку

- Файл:функция: `app/api/routes.py:48` `delete_link`.
- Успех: `204 No Content` (пустое тело).
- Тесты: `test_delete_link_returns_204`, `test_delete_link_nonexistent_returns_404`,
  `test_delete_link_removes_from_db`.

### `GET /{short_code}` — редирект

- Файл:функция: `app/main.py:12` `redirect_to_target`.
- Успех: `307 Temporary Redirect`, заголовок `Location: <target_url>`.
- Инкрементирует `clicks` только для активной ссылки.
- Тесты: `test_redirect_active_link_returns_307`, `test_redirect_increments_clicks`,
  `test_redirect_nonexistent_returns_404`, `test_redirect_expired_link_returns_410`,
  `test_redirect_disabled_link_returns_404`, `test_redirect_404_for_nonexistent_code`
  — `tests/integration/test_redirect.py`.

## Схема ответа `LinkResponse`

`app/api/schemas.py:16-24`:

| Поле | Тип | Примечание |
|---|---|---|
| `id` | `int` | |
| `short_code` | `str` | |
| `target_url` | `str` | |
| `short_url` | `str` | `{base_url}/{short_code}`, собирается в `to_response` (`app/api/deps.py:35`) |
| `status` | `str` | `"active"`/`"expired"`/`"disabled"`, вычисляется на момент `now` |
| `clicks` | `int` | |
| `created_at` | `datetime` | |
| `expires_at` | `datetime \| None` | |
| `disabled` | `bool` | |

`to_response` поднимает `ValueError("cannot serialize an unsaved link")` при
`link.id is None` — `app/api/deps.py:27-28`. Подтверждено
`test_to_response_without_id_raises` (`tests/unit/test_api_deps.py:62`).

## Маппинг доменных ошибок в HTTP

`app/api/errors.py:17-24`, словарь `_STATUS_BY_ERROR`; функция
`raise_for_domain_error` (`app/api/errors.py:27`):

| Доменная ошибка | HTTP | Тест |
|---|---|---|
| `InvalidUrlError` | 422 | `test_raise_for_invalid_url_error_returns_422` |
| `InvalidShortCodeError` | 422 | `test_raise_for_invalid_short_code_error_returns_422` |
| `ShortCodeTakenError` | 409 | `test_raise_for_short_code_taken_error_returns_409` |
| `LinkNotFoundError` | 404 | `test_raise_for_link_not_found_error_returns_404` |
| `LinkExpiredError` | 410 | `test_raise_for_link_expired_error_returns_410` |
| `LinkDisabledError` | 404 | `test_raise_for_link_disabled_error_returns_404` |
| неизвестный наследник `DomainError` | 500 | `test_raise_for_unknown_domain_error_returns_500` |

Оригинал сохраняется как `__cause__` — `test_raise_for_domain_error_preserves_cause`.

## OpenAPI-схема

> Пробел: правила `.agents/agents/docs.md` упоминают ссылку на `/schema/swagger` в
> README, но `README.md` в репозитории отсутствует. FastAPI автоматически отдаёт
> схему на `/openapi.json` и `/docs` — это стандартное поведение фреймворка
> ([../../raw/fastapi.md](../../raw/fastapi.md)), но в коде приложения явная настройка
> URL-ов OpenAPI не переопределяется (`app/main.py:23-26` использует дефолты).

## Связанные страницы

- [../domain/links.md](../domain/links.md) — доменные правила и инварианты.
- [database.md](database.md) — персистентное состояние.
- [../decisions.md](../decisions.md) — решение по верхней границе TTL.
