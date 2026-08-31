# Skill: Code Review

## Цель

Проверить что код соответствует стандартам из `.agents/agents/python-standards.md`
и архитектурным правилам из `.agents/agents/architecture.md`.

***

## Алгоритм

### 1. Запустить автоматические проверки

~~~bash
uv run ruff check <файл_или_папка>
uv run basedpyright <файл_или_папка>
~~~

Включить результаты в отчёт. Автоматические ошибки не пересказывать — только итог.

### 2. Прочитать файлы под ревью полностью

### 3. Проверить по чеклисту

#### 🔴 Блокирующие (merge запрещён до исправления)

- [ ] `from __future__ import annotations` — первая строка в файле
- [ ] Все параметры функций аннотированы
- [ ] Все функции имеют аннотацию возвращаемого типа (включая `-> None`)
- [ ] Нет `Optional[X]`, `List[X]`, `Dict[K,V]` — только `X | None`, `list[X]`, `dict[K,V]`
- [ ] Нет `-> dict` как публичного контракта — только DTO/Value Object
- [ ] Сервисный слой не импортирует `db/models.py` напрямую
- [ ] Бизнес-логика не в route handlers
- [ ] Нет `except Exception: pass`
- [ ] Нет мутируемых значений по умолчанию (`= []`, `= {}`)
- [ ] **Async-правила (§5):** проект полностью async — нет `from sqlalchemy.orm import Session` (только `AsyncSession`), все DB-методы `async def` + `await session.execute(...)`, сервис вызывает репозиторий через `await`, handler'ы `async def` + `await service.X(...)`. Sync-вызов в async-контексте блокирует event loop и валит производительность.
- [ ] **Никаких `next(generator_func())` для async-генераторов** — это просто не работает (нужен `anext()` или `async for`). Признак copy-paste из старого sync-кода.
- [ ] **Логирование (§13):** нет `print()`, нет f-строк в `logger.info(...)`, нет секретов / токенов / Authorization в kwargs.
- [ ] **Безопасность (§14):** нет хардкода секретов, SQL параметризован, пароли через `bcrypt`/`argon2`, HTTP-клиенты с `timeout=` и `verify=True`, `subprocess` без `shell=True` с user input.

#### 🟡 Некритичные (рекомендации, исправить в следующем PR)

- [ ] Нет магических чисел — только именованные константы
- [ ] Нет дублирования логики (DRY)
- [ ] Функция делает одно дело (SRP), не длиннее 30-40 строк
- [ ] Именование: `snake_case` / `PascalCase` / `UPPER_SNAKE_CASE`
- [ ] Параллельные задачи через `asyncio.TaskGroup`, не `gather()` (когда не нужен `return_exceptions=True`) — §5
- [ ] Современный синтаксис: `type UserId = int` (PEP 695), `Self`, `match/case`, `StrEnum` где уместно — §15
- [ ] Coverage приложения остаётся 100% (`--cov-fail-under=100`)

***

## Формат отчёта

~~~text
## Code Review: <файл или ветка>

### Автоматические проверки
ruff: X ошибок | basedpyright: Y ошибок

### Нарушения

#### 🔴 Блокирующие

| # | Файл | Строка | Нарушение | Стандарт |
|---|------|--------|-----------|----------|
| 1 | bad_link_service.py | 1 | Отсутствует `from __future__ import annotations` | python-standards §1 |

#### 🟡 Некритичные

| # | Файл | Строка | Нарушение | Стандарт |
|---|------|--------|-----------|----------|
| 1 | bad_link_service.py | 45 | Магическое число `75` | python-standards §8 |

### Итог
- Блокирующих: X
- Рекомендаций: Y
- Вердикт: ❌ Требует правок / ✅ Можно принимать
~~~

***

## Пример промпта

~~~text
Прочитай файл .skills/code-review.md (он сам ссылается на .agents/agents/python-standards.md, .agents/agents/code.md и .agents/agents/architecture.md).

Проведи code review файла app/services/bad_link_service.py.

Сначала запусти:
uv run ruff check app/services/bad_link_service.py
uv run basedpyright app/services/bad_link_service.py

Затем проведи ручную проверку по чеклисту из .skills/code-review.md.
Сформируй отчёт в формате из .skills/code-review.md.
~~~
