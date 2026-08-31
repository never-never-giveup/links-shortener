# Bugfix

---

## Вариант A — субмодуль в проекте (`.agents/`)

```text
Jira: <JIRA-KEY>
Дефект: <одна строка — что ломается и как проявляется>

Прочитай .agents/AGENTS.md, .agents/agents/testing.md, .agents/agents/docs.md,
.agents/skills/bugfix.md и .agents/skills/docs.md.

Создай ветку с именем РОВНО `bugfix/<JIRA-KEY>-<slug>`.

Воспроизведи дефект:
1. Найди затронутый код — прочитай файлы, трейсбек, логи.
2. Определи корневую причину (не симптом).

Исправь:
3. Сначала напиши regression test — он должен падать до фикса.
4. Внеси минимальный фикс — только то что нужно, никакого попутного рефакторинга.
5. Убедись что regression test стал зелёным.
6. Убедись что существующие тесты не сломались.

Документация (по .agents/skills/docs.md):
7. Запись в CHANGELOG.md под [Unreleased] → Fixed с Jira-тикетом.
8. Обнови docstring если изменилась семантика метода.

После прогони:
uv run ruff check .
uv run basedpyright
uv run pytest -q
```

---

## Вариант B — запуск из ai-sdlc-rules напрямую

```text
Jira: <JIRA-KEY>
Дефект: <одна строка — что ломается и как проявляется>
Проект: <путь к репозиторию>

Прочитай AGENTS.md, agents/testing.md, agents/docs.md,
skills/bugfix.md и skills/docs.md.

Создай ветку с именем РОВНО `bugfix/<JIRA-KEY>-<slug>`.

Воспроизведи дефект:
1. Найди затронутый код — прочитай файлы, трейсбек, логи.
2. Определи корневую причину (не симптом).

Исправь:
3. Сначала напиши regression test — он должен падать до фикса.
4. Внеси минимальный фикс — только то что нужно, никакого попутного рефакторинга.
5. Убедись что regression test стал зелёным.
6. Убедись что существующие тесты не сломались.

Документация (по skills/docs.md):
7. Запись в CHANGELOG.md под [Unreleased] → Fixed с Jira-тикетом.
8. Обнови docstring если изменилась семантика метода.

После прогони:
uv run ruff check .
uv run basedpyright
uv run pytest -q
```
