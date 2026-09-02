# Skill: Integration Tests

## Алгоритм написания integration тестов

### 1. Подготовка
- Прочитать `.agents/agents/testing.md` и `.agents/agents/database.md`.
- Integration тесты проверяют **полный путь**: HTTP-запрос → API → Service → Repository → PostgreSQL.
- **Проект полностью async**: handler'ы async, сервис async, репозиторий async, `AsyncSession` через DI.

### 2. Структура
- Файлы: `tests/integration/test_<endpoint>.py`.
- HTTP-клиент: **`httpx.AsyncClient`** поверх `ASGITransport` (он async и поддерживает `async with`). Старый sync-клиент не использовать: он прячет async-ошибки и хуже подходит для strict async-проекта.
- Реальная тестовая БД (PostgreSQL в Docker).
- **autouse-фикстура очистки таблицы — async**, выполняется через `async with SessionLocal() as session: await session.execute(text("DELETE FROM links"))`.

### 3. Правила
- Только `pytest`, функции. Никакого `unittest.TestCase`.
- **Все тестовые функции `async def`** — `asyncio_mode = "auto"` в `pyproject.toml` запустит их без `@pytest.mark.asyncio`.
- **autouse-фикстура очистки — тоже `async`**:
  ```python
  @pytest.fixture(autouse=True)
  async def clean_db() -> AsyncGenerator[None, None]:
      async with SessionLocal() as session:
          await session.execute(text("DELETE FROM links"))
          await session.commit()
      yield
      async with SessionLocal() as session:
          await session.execute(text("DELETE FROM links"))
          await session.commit()
```
- **AsyncClient вызывается через `async with`** или через создание клиента в фикстуре. **`follow_redirects=False`** обязателен — нам нужно проверить именно 302 и `Location`, а не финальный ответ.
- Не зависеть от порядка выполнения тестов.
- Аннотации `-> None` у каждой тестовой функции, `async def`.
- `from __future__ import annotations` первой строкой файла.

### Пример теста (async + httpx.AsyncClient)

```python
from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.db.session import SessionLocal
from app.main import app


@pytest.fixture(autouse=True)
async def clean_db() -> AsyncGenerator[None, None]:
    async with SessionLocal() as session:
        await session.execute(text("DELETE FROM links"))
        await session.commit()
    yield
    async with SessionLocal() as session:
        await session.execute(text("DELETE FROM links"))
        await session.commit()


async def test_post_link_returns_201() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        response = await client.post("/links/", json={"url": "https://example.com"})
        assert response.status_code == 201
        body = response.json()
        assert body["code"]
        assert body["original_url"] == "https://example.com"
        assert body["clicks"] == 0
```

### 4. Что тестировать

**Не только happy path.** На каждый эндпоинт должны быть тесты для трёх категорий:

- **Happy path** — валидный запрос → ожидаемый успех (200/201, корректное тело JSON, данные в БД).
- **Граничные случаи (boundary)** — значения **на краю** допустимого диапазона. Например для URL длиной 2048 (максимум) — должен принять; для URL длиной 2049 — должен отказать. Boundary-тесты ловят off-by-one ошибки.
- **Невалидный ввод** — что возвращает API на пустой URL, на `"not-a-url"`, на missing-field, на slash в конце, на превышение лимитов. Ожидаем 422 (а не 500). На несуществующий ресурс — 404.

Плюс при багфиксе — **regression test** на конкретную проблему (см. `.skills/bugfix.md`).

Конкретные пункты:

- Все HTTP-методы эндпоинта (GET, POST, PUT/PATCH, DELETE).
- Коды ответов (200, 201, 404, 422) — все ветки, не только успешная.
- Тело ответа — структура JSON, проверять конкретные поля (`assert body["code"]`, не только `body is not None`).
- Что данные реально сохраняются/удаляются в БД (через `await session.execute(select(...))` после запроса).
- Заголовки ответа когда они важны (Location на 302-редиректе, Content-Type на JSON-ответе).

### 5. Проверка
- `uv run ruff format .` — автоформатирование.
- `uv run ruff check --fix .` — автофикс автофиксимых правил.
- `uv run ruff check .` — должно быть зелёно.
- `uv run basedpyright`
- `uv run pytest tests/integration/ -q` — все тесты зелёные, без warnings про event loop или sync-в-async.

### 6. Coverage и отчёт

Coverage — обязательный гейт, а не справочная цифра. Для полного тестового контура выполни:

```bash
uv run pytest --cov=app --cov-branch --cov-report=term-missing --cov-fail-under=100
```

Для ограниченной задачи замени `app` на явно названный Python-модуль. Объявленная область
должна получить 100% строк и ветвей. Нельзя менять `app/`, `pyproject.toml`, coverage-исключения,
использовать `skip`, `xfail`, `pragma: no cover` или пустые проверки ради процента.

Сохрани `reviews/<задача>-coverage.md` со следующими доказательствами:

- точная команда и дата запуска;
- проверенный commit SHA;
- число `passed` и итоговый процент;
- значение `Missing` (`none` при 100%);
- какие endpoint'ы и уровни тестов добавлены;
- подтверждение отсутствия `skip`, `xfail`, `pragma: no cover` и бессодержательных `assert`.

Задача не завершена, пока coverage ниже 100%, проверки красные или отчёт не сохранён.
