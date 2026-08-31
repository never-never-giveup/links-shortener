# Skill: Unit Tests

## Алгоритм написания unit тестов

### 1. Подготовка
- Прочитать `.agents/agents/testing.md` — стратегия тестирования.
- Unit тесты тестируют **сервисный слой** изолированно от БД.
- **Проект полностью async**: `LinkService` — async, `LinkRepository` — async. Тесты тоже async.

### 2. Структура
- Файлы: `tests/unit/test_<module>.py`.
- Фабрика: `make_service()` создаёт сервис с **Fake**-репозиторием.
- Fake-репозиторий: хранит данные в обычном `dict` — без БД, **с теми же async-сигнатурами** что у реального `LinkRepository` (методы `async def`, иначе `await self.repository.X(...)` в сервисе сломается).

### 3. Правила
- Только `pytest`, функции. Никакого `unittest.TestCase`.
- **Все тестовые функции `async def`** — у нас в `pyproject.toml` стоит `asyncio_mode = "auto"`, pytest сам запускает их в event loop без `@pytest.mark.asyncio`.
- Моки — только Fake-классы. Никакого `MagicMock`, `patch`.
- Fake-репозиторий — **все методы `async def`**, даже если внутри просто `return self._store[code]`. Сигнатуры должны соответствовать реальному `LinkRepository` (`add`, `get_by_code`, `increment_clicks`, `list_active`, `get_by_id`, `archive` — все async).
- Каждый тест создаёт свой экземпляр сервиса через фабрику.
- Аннотации `-> None` у каждой тестовой функции.
- `pytest.raises(ErrorClass, match=...)` — обязательно с `match=` и фрагментом сообщения.
- `from __future__ import annotations` первой строкой файла.

### 4. Что тестировать
- Успешный путь (happy path).
- Граничные случаи (пустая строка, None, дубликаты).
- Ошибочные случаи (несуществующий ID, невалидный ввод).

### Пример Fake-репозитория (async)

```python
class FakeLinkRepository:
    def __init__(self) -> None:
        self._store: dict[str, Link] = {}
        self._by_id: dict[int, Link] = {}
        self._next_id: int = 1

    async def add(self, code: str, original_url: str) -> Link:
        link = Link(
            id=self._next_id,
            code=code,
            original_url=original_url,
            clicks=0,
            created_at=datetime.now(timezone.utc),
            archived_at=None,
        )
        self._store[code] = link
        self._by_id[self._next_id] = link
        self._next_id += 1
        return link

    async def get_by_code(self, code: str) -> Link | None:
        return self._store.get(code)

    async def increment_clicks(self, code: str) -> Link | None:
        link = self._store.get(code)
        if link is None or link.archived_at is not None:
            return None
        updated = replace(link, clicks=link.clicks + 1)
        self._store[code] = updated
        self._by_id[updated.id] = updated
        return updated
```

### Пример теста (async)

```python
async def test_create_valid_url_returns_link() -> None:
    service = make_service()
    link = await service.create("https://example.com")
    assert link.code
    assert link.original_url == "https://example.com"


async def test_create_invalid_url_raises() -> None:
    service = make_service()
    with pytest.raises(ValueError, match="Invalid URL"):
        await service.create("not-a-url")
```

### 5. Проверка

**Шаг проверки обязателен — задача не считается завершённой, пока все команды ниже не выполнены и их вывод не показан.**

- `uv run ruff format .` — автоформатирование.
- `uv run ruff check --fix .` — автофикс автофиксимых правил (`I001`, `F401` и др.).
- `uv run ruff check .` — должно быть зелёно.
- `uv run pytest tests/unit/ -q` — **запустить pytest через инструмент выполнения команд и показать вывод**. Не утверждать «тесты пройдут» без реального запуска.
- Если pytest упал (IndentationError, SyntaxError, ImportError, AssertionError, AttributeError) — **исправить файл и перезапустить pytest**. Повторять пока не будет `passed`.
- В финальном ответе привести строку итога pytest (`N passed in Xs` или `N failed`) — иначе задача не выполнена.

### 6. Coverage и отчёт

Для unit-задачи измеряй именно тестируемый модуль. Например для `LinkService`:

```bash
uv run pytest tests/unit/test_link_service.py --cov=app.services.link_service --cov-branch --cov-report=term-missing --cov-fail-under=100
```

Для финального тестового контура всего проекта обязательна команда:

```bash
uv run pytest --cov=app --cov-branch --cov-report=term-missing --cov-fail-under=100
```

Нельзя менять `app/`, `pyproject.toml`, coverage-исключения, использовать `skip`, `xfail`,
`pragma: no cover` или пустые проверки ради процента.

Сохрани `reviews/<задача>-coverage.md`: точная команда, дата, проверенный commit SHA,
число `passed`, процент, `Missing` (`none` при 100%), покрытые сценарии и подтверждение
отсутствия запрещённых обходов. Задача не завершена, пока объявленная область не имеет
100% branch coverage, проверки красные или отчёт не сохранён.
