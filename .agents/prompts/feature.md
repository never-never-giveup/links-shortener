# Новая фича

---

## Вариант A — субмодуль в проекте (`.agents/`)

```text
Jira: <JIRA-KEY>
Задача: <описание фичи>

Прочитай .agents/AGENTS.md, .agents/agents/code.md, .agents/agents/docs.md,
.agents/skills/feature.md и .agents/skills/docs.md.

Создай ветку с именем РОВНО `feature/<JIRA-KEY>-<slug>`.

Изучи структуру проекта: api/, services/, db/, domain/ (или аналогичные).
Найди существующие точки расширения — не дублируй логику.

Реализуй по слоям в таком порядке:
1. domain/ — добавь или расширь dataclass / TypeAlias / Pydantic-модель.
2. db/ — добавь поле в SQLAlchemy-модель если нужно; создай Alembic-миграцию.
3. repositories/link_repository.py — добавь метод репозитория (+ маппинг ORM ↔ домен).
4. services/ — реализуй бизнес-логику.
5. api/ — добавь эндпоинт.

Тесты:
6. Unit-тест для сервисного слоя (Fake-репозиторий, без БД).
7. Integration-тест для API (TestClient + реальная БД).

Документация (по .agents/skills/docs.md):
8. Docstring на новые публичные методы (Google-style, на русском).
9. Запись в CHANGELOG.md под [Unreleased] → Added.
10. Обнови README если изменился список эндпоинтов или ENV.

После реализации прогони:
uv run ruff check .
uv run basedpyright
uv run pytest -q
```

---

## Вариант B — запуск из ai-sdlc-rules напрямую

```text
Jira: <JIRA-KEY>
Задача: <описание фичи>
Проект: <путь к репозиторию>

Прочитай AGENTS.md, agents/code.md, agents/docs.md,
skills/feature.md и skills/docs.md.

Создай ветку с именем РОВНО `feature/<JIRA-KEY>-<slug>`.

Изучи структуру проекта по указанному пути.
Найди существующие точки расширения — не дублируй логику.

Реализуй по слоям в таком порядке:
1. domain/ — добавь или расширь dataclass / TypeAlias / Pydantic-модель.
2. db/ — добавь поле в SQLAlchemy-модель если нужно; создай Alembic-миграцию.
3. repositories/link_repository.py — добавь метод репозитория (+ маппинг ORM ↔ домен).
4. services/ — реализуй бизнес-логику.
5. api/ — добавь эндпоинт.

Тесты:
6. Unit-тест для сервисного слоя (Fake-репозиторий, без БД).
7. Integration-тест для API (TestClient + реальная БД).

Документация (по skills/docs.md):
8. Docstring на новые публичные методы (Google-style, на русском).
9. Запись в CHANGELOG.md под [Unreleased] → Added.
10. Обнови README если изменился список эндпоинтов или ENV.

После реализации прогони:
uv run ruff check .
uv run basedpyright
uv run pytest -q
```
