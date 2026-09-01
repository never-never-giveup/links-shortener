# Test Coverage Report

## Команда покрытия

```bash
uv run pytest --cov=app --cov-branch --cov-report=term-missing --cov-fail-under=100
```

## Дата

2025-09-02

## Проверенный коммит

`bb6ba18`

## Результаты

| Показатель         | Значение       |
|--------------------|----------------|
| Passed             | 103            |
| Failed             | 0              |
| Coverage (строки)  | 100%           |
| Coverage (ветви)   | 100%           |
| Missing            | none           |

## Таблица покрытия по модулям

| Модуль                        | Stmts | Miss | Branch | BrPart | Cover |
|-------------------------------|-------|------|--------|--------|-------|
| app/__init__.py               | 0     | 0    | 0      | 0      | 100%  |
| app/api/__init__.py           | 0     | 0    | 0      | 0      | 100%  |
| app/api/deps.py               | 21    | 0    | 2      | 0      | 100%  |
| app/api/errors.py             | 8     | 0    | 0      | 0      | 100%  |
| app/api/routes.py             | 32    | 0    | 0      | 0      | 100%  |
| app/api/schemas.py            | 17    | 0    | 0      | 0      | 100%  |
| app/config.py                 | 9     | 0    | 0      | 0      | 100%  |
| app/db/__init__.py            | 0     | 0    | 0      | 0      | 100%  |
| app/db/base.py                | 3     | 0    | 0      | 0      | 100%  |
| app/db/models.py              | 14    | 0    | 0      | 0      | 100%  |
| app/db/session.py             | 19    | 0    | 2      | 0      | 100%  |
| app/domain/__init__.py        | 0     | 0    | 0      | 0      | 100%  |
| app/domain/errors.py          | 26    | 0    | 0      | 0      | 100%  |
| app/domain/link.py            | 31    | 0    | 4      | 0      | 100%  |
| app/domain/value_objects.py   | 50    | 0    | 18     | 0      | 100%  |
| app/main.py                   | 19    | 0    | 0      | 0      | 100%  |
| app/repositories/__init__.py  | 0     | 0    | 0      | 0      | 100%  |
| app/repositories/link_repository.py | 28 | 0 | 0    | 0      | 100%  |
| app/services/__init__.py      | 0     | 0    | 0      | 0      | 100%  |
| app/services/link_service.py  | 41    | 0    | 10     | 0      | 100%  |
| **TOTAL**                     | 318   | 0    | 36     | 0      | 100%  |

## Уровни тестов

| Уровень            | Файл                                    | Число тестов |
|--------------------|-----------------------------------------|-------------|
| Unit (сервис)      | tests/unit/test_link_service.py         | 17          |
| Unit (сущность)    | tests/unit/test_link_entity.py          | 11          |
| Unit (value obj)   | tests/unit/test_value_objects.py        | 30          |
| Unit (ошибки)      | tests/unit/test_domain_errors.py        | 10          |
| Unit (deps)        | tests/unit/test_api_deps.py             | 7           |
| Unit (api errors)  | tests/unit/test_api_errors.py           | 8           |
| Integration (API)  | tests/integration/test_links_api.py     | 14          |
| Integration (redir)| tests/integration/test_redirect.py      | 6           |

## Проверка качества кода

- **Ruff**: 0 errors
- **BasedPyright**: 0 errors, 0 warnings

## Подтверждение отсутствия запрещённых обходов

- `pytest.skip` — отсутствует
- `xfail` — отсутствует
- `pragma: no cover` — отсутствует
- `MagicMock`, `patch`, `unittest.mock` — не используются (только Fake-объекты)
- Бессодержательные `assert` — отсутствуют
