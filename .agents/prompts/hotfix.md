# Hotfix

Срочный фикс в прод. Минимальный скоуп — только то что нужно для фикса.

---

## Вариант A — субмодуль в проекте (`.agents/`)

```text
Jira: <JIRA-KEY>
Инцидент: <что упало в проде, как проявляется>

Прочитай .agents/AGENTS.md, .agents/agents/hotfix.md, .agents/agents/docs.md,
.agents/skills/hotfix.md и .agents/skills/docs.md.

Создай ветку от main с именем РОВНО `hotfix/<JIRA-KEY>-<slug>`.

Правила hotfix (из .agents/agents/hotfix.md):
- Минимальный scope — меняй только то что нужно для фикса.
- Никакого попутного рефакторинга или cleanup.
- Обязательный regression test в том же коммите.

Сделай:
1. Regression test — должен падать до фикса, стать зелёным после.
2. Минимальный фикс — не более 2-3 файлов.
3. Проверь что существующие тесты не сломались.

Документация (минимум для hotfix):
4. Одна строка в CHANGELOG.md → Fixed с Jira-тикетом.
   README / ADR / docstring расширения — не трогать.

После прогони:
uv run ruff check .
uv run basedpyright
uv run pytest -q
```

---

## Вариант B — запуск из ai-sdlc-rules напрямую

```text
Jira: <JIRA-KEY>
Инцидент: <что упало в проде, как проявляется>
Проект: <путь к репозиторию>

Прочитай AGENTS.md, agents/hotfix.md, agents/docs.md,
skills/hotfix.md и skills/docs.md.

Создай ветку от main с именем РОВНО `hotfix/<JIRA-KEY>-<slug>`.

Правила hotfix:
- Минимальный scope — меняй только то что нужно для фикса.
- Никакого попутного рефакторинга или cleanup.
- Обязательный regression test в том же коммите.

Сделай:
1. Regression test — должен падать до фикса, стать зелёным после.
2. Минимальный фикс — не более 2-3 файлов.
3. Проверь что существующие тесты не сломались.

Документация (минимум для hotfix):
4. Одна строка в CHANGELOG.md → Fixed с Jира-тикетом.
   README / ADR / docstring расширения — не трогать.

После прогони:
uv run ruff check .
uv run basedpyright
uv run pytest -q
```
