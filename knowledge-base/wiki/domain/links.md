# Domain: Links

> Страница вики. Уровень: доменные правила и инварианты. Источник фактов — `app/domain/`.

## Сущность `Link`

`app/domain/link.py:17-46`. Неизменяемый dataclass (`frozen=True, slots=True`).

| Поле | Тип | Значение |
|---|---|---|
| `short_code` | `ShortCode` | короткий код |
| `target_url` | `TargetUrl` | URL назначения |
| `created_at` | `datetime` | время создания |
| `expires_at` | `datetime \| None` | срок жизни (`None` = бессрочно) |
| `clicks` | `int` | счётчик переходов, по умолчанию `0` |
| `disabled` | `bool` | ручное отключение, по умолчанию `False` |
| `id` | `int \| None` | идентификатор БД, `None` до сохранения |

### Поведение

- `status(now)` → `LinkStatus` (`app/domain/link.py:29`): приоритет `DISABLED` над
  `EXPIRED` (если `disabled=True` — статус `disabled` даже при истёкшем TTL).
  Подтверждено тестом `test_link_status_expired_disabled_returns_disabled`
  (`tests/unit/test_link_entity.py:42`).
- `is_active(now)` → `bool` (`app/domain/link.py:37`): `True` только если статус
  `ACTIVE`.
- `with_click()` → `Self` (`app/domain/link.py:40`): возвращает копию с `clicks+1`,
  оригинал не меняется. Подтверждено `test_link_with_click_increments_clicks`
  (`tests/unit/test_link_entity.py:67`).
- `disable()` → `Self` (`app/domain/link.py:44`): возвращает копию с `disabled=True`.
  Подтверждено `test_link_disable_returns_disabled_copy` (`tests/unit/test_link_entity.py:74`).

### `LinkStatus` (StrEnum)

`app/domain/link.py:11-14`: `ACTIVE="active"`, `EXPIRED="expired"`, `DISABLED="disabled"`.

## Value object `TargetUrl`

`app/domain/value_objects.py:41-61`. Неизменяемый. Инварианты (в `__post_init__`):

| Правило | Реакция | Тест |
|---|---|---|
| непустой после `.strip()` | `InvalidUrlError("empty")` | `test_targeturl_empty_raises` |
| длина ≤ `MAX_URL_LENGTH` (2048) | `InvalidUrlError("longer than ...")` | `test_targeturl_too_long_raises` |
| схема ∈ `{http, https}` | `InvalidUrlError("scheme must be http or https")` | `test_targeturl_no_scheme_raises`, `test_targeturl_ftp_scheme_raises` |
| присутствует host | `InvalidUrlError("missing host")` | `test_targeturl_missing_host_raises` |
| без учётных данных в URL | `InvalidUrlError("credentials in URL are not allowed")` | `test_targeturl_credentials_raises` |
| SSRF-фильтр (см. ниже) | `InvalidUrlError(...)` | `test_targeturl_*_raises` |

Константы: `MAX_URL_LENGTH=2048`, `ALLOWED_SCHEMES={"http","https"}` —
`app/domain/value_objects.py:10-11`.

### SSRF-фильтр `_reject_ssrf`

`app/domain/value_objects.py:21-38`. Статическая блокировка (без DNS-резолва):

- Имена `localhost`, `ip6-localhost` → `InvalidUrlError("loopback host is not allowed")`.
- IP-адрес, если `is_loopback`/`is_private`/`is_link_local`/`is_reserved`/
  `is_multicast`/`is_unspecified` → `InvalidUrlError("private or reserved IP is not allowed")`.
- Публичный IP (например `8.8.8.8`) разрешён — `test_targeturl_public_ip_succeeds`.

## Value object `ShortCode`

`app/domain/value_objects.py:64-75`. Неизменяемый. Инварианты:

| Правило | Реакция | Тест |
|---|---|---|
| длина 4..16 (`MIN_CODE_LENGTH`..`MAX_CODE_LENGTH`) | `InvalidShortCodeError("length must be 4..16")` | `test_short_code_too_short_raises`, `test_short_code_too_long_raises` |
| только `[A-Za-z0-9]` (`CODE_ALPHABET`) | `InvalidShortCodeError("only ASCII letters and digits are allowed")` | `test_short_code_invalid_chars_raises` |

Константы: `CODE_ALPHABET = ascii_letters + digits`, `MIN_CODE_LENGTH=4`,
`MAX_CODE_LENGTH=16`, `DEFAULT_CODE_LENGTH=7` —
`app/domain/value_objects.py:14-18`.

## Генерация кода

`app/domain/codegen.py:8-10`, функция `generate_short_code(code_length=DEFAULT_CODE_LENGTH)`:
`secrets.choice(CODE_ALPHABET)` — криптостойкий генератор. Длина по умолчанию — 7
символов. Поведение подтверждено `test_create_link_with_generated_code_returns_link`
(`tests/unit/test_link_service.py:60`): `len(link.short_code.value) == 7`.

## Доменные ошибки

`app/domain/errors.py`. Базовый класс `DomainError(Exception)` (строка 4). Наследники
(каждый хранит контекст в атрибуте):

| Ошибка | Атрибут | Текст | Тест сообщения |
|---|---|---|---|
| `InvalidUrlError` | `reason` | `Invalid target URL: {reason}` | `test_invalid_url_error_message` |
| `InvalidShortCodeError` | `reason` | `Invalid short code: {reason}` | `test_invalid_short_code_error_message` |
| `ShortCodeTakenError` | `short_code` | `Short code already taken: {short_code}` | `test_short_code_taken_error_message` |
| `LinkNotFoundError` | `short_code` | `Link not found: {short_code}` | `test_link_not_found_error_message` |
| `LinkExpiredError` | `short_code` | `Link expired: {short_code}` | `test_link_expired_error_message` |
| `LinkDisabledError` | `short_code` | `Link disabled: {short_code}` | `test_link_disabled_error_message` |

Все наследуются от `DomainError` — `test_all_domain_errors_inherit_from_domain_error`.

## Бизнес-правила в `LinkService`

`app/services/link_service.py`, класс `LinkService` (строка 27).

| Операция | Правило | Где | Тест |
|---|---|---|---|
| `create_link` | custom_code занят → `ShortCodeTakenError` | `:45-48` | `test_create_link_with_taken_custom_code_raises` |
| `create_link` | TTL ≤ 0 → без `expires_at` (None) | `:51-53` | `test_create_link_with_zero_ttl_has_no_expiry`, `..._negative_ttl_...` |
| `create_link` | TTL > 0 → `expires_at = now + timedelta(seconds=ttl)` | `:51-53` | `test_create_link_with_ttl_sets_expires_at` |
| `get_link` | не найден → `LinkNotFoundError` | `:62-66` | `test_get_link_nonexistent_raises` |
| `list_links` | лимит по умолчанию 100 | `:68-69` | `test_list_links_respects_limit` |
| `resolve` | expired → `LinkExpiredError`; disabled → `LinkDisabledError`; иначе инкремент `clicks` | `:71-79` | `test_resolve_expired_link_raises`, `test_resolve_disabled_link_raises`, `test_resolve_active_link_increments_clicks` |
| `disable_link` | не найден → `LinkNotFoundError` | `:81-83` | `test_disable_link_nonexistent_raises` |
| `delete_link` | не найден → `LinkNotFoundError` | `:85-89` | `test_delete_link_nonexistent_raises` |

> Внешний контракт TTL-валидации (верхняя граница 86400) живёт на транспортном
> слое в `CreateLinkRequest` — см. [../contracts/http-api.md](../contracts/http-api.md).

## Связанные страницы

- [../contracts/http-api.md](../contracts/http-api.md) — маппинг ошибок в HTTP-коды.
- [../contracts/database.md](../contracts/database.md) — маппинг домена в таблицу.
- [../decisions.md](../decisions.md) — решения по TTL-границам.

## Пробелы

- `create_link` не проверяет, что сгенерированный код не совпадает с уже
  существующим (коллизия). При `code_length=7` и алфавите 62 символа пространство
  велико, но явной retry-логики нет — `app/services/link_service.py:49-50`.
  См. [../decisions.md](../decisions.md).
