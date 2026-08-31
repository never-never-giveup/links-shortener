# Code Review

---

## Вариант A — субмодуль в проекте (`.agents/`)

```text
Прочитай .agents/skills/code-review.md (он ссылается на
.agents/agents/python-standards.md, .agents/agents/code.md, .agents/agents/architecture.md).

Проведи code review <файла или ветки>.

Сначала запусти автоматические проверки:
uv run ruff check <путь>
uv run basedpyright <путь>

Затем ручная проверка по чеклисту из .agents/skills/code-review.md.

Сформируй отчёт строго в формате из .agents/skills/code-review.md:
- Секция автоматических проверок (ruff / basedpyright: N ошибок)
- Таблица 🔴 блокирующих нарушений с номерами строк и ссылкой на стандарт
- Таблица 🟡 некритичных замечаний
- Итог: Approve / Changes requested

Не правь исходный файл — только отчёт.
```

---

## Вариант B — запуск из ai-sdlc-rules напрямую

```text
Прочитай skills/code-review.md (он ссылается на
agents/python-standards.md, agents/code.md, agents/architecture.md).

Проведи code review <файла или ветки> в проекте <путь к репозиторию>.

Сначала запусти автоматические проверки:
uv run ruff check <путь>
uv run basedpyright <путь>

Затем ручная проверка по чеклисту из skills/code-review.md.

Сформируй отчёт строго в формате из skills/code-review.md:
- Секция автоматических проверок (ruff / basedpyright: N ошибок)
- Таблица 🔴 блокирующих нарушений с номерами строк и ссылкой на стандарт
- Таблица 🟡 некритичных замечаний
- Итог: Approve / Changes requested

Не правь исходный файл — только отчёт.
```
