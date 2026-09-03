# LOG — журнал событий базы знаний

Append-only. Свежее событие — сверху. Формат записи:
`ГГГГ-ММ-ДД | <тип> | <что> | <где> | <контекст>`.

- 2026-09-03 | ingest | Заземлена атрибуция метода LLM Wiki: добавлена карточка raw/llm-wiki.md (Andrej Karpathy, gist.github.com/karpathy/...94f, дата проверки 2026-09-03), исправлено «А. Карпаф» → «Андрей Карпати» со ссылкой на карточку | raw/llm-wiki.md, AGENTS.md, INDEX.md, raw/README.md | исправление пробела в атрибуции
- 2026-09-03 | update | Починена оборванная lint-секция в AGENTS.md: пункт «Битые ссылки» получил конкретную команду проверки (rg/сортировка путей + альтернатива mdformat) | knowledge-base/AGENTS.md | было: после «Проверка:» не было ни команды, ни описания
- 2026-09-03 | ingest | Добавлен скилл `.agents/skills/knowledge-base.md` — алгоритм filing back, привязанный к конвейеру задач (триггеры, шаги, lint, LOG) | .agents/skills/ | закрывает разрыв между правилами KB в knowledge-base/AGENTS.md и скиллами в .agents/skills/, которые про KB не упоминали
- 2026-09-03 | update | В скиллы feature/bugfix/refactoring/hotfix/docs добавлен шаг «Актуализация базы знаний» со ссылкой на .agents/skills/knowledge-base.md | .agents/skills/*.md | нумерация последующих шагов сдвинута: feature 6→7→8, bugfix 6→7→8, refactoring 5→6→7, hotfix 5→6→7, docs +шаг 5
- 2026-09-03 | ingest | Первоначальная сборка базы знаний: raw/ (6 карточек внешних источников) + wiki/ (8 страниц) + AGENTS.md + INDEX.md + LOG.md | knowledge-base/ | ветка workshop/project-knowledge-base, off main; код приложения не изменялся
- 2026-09-03 | ingest | Зафиксированы внешние первоисточники: conventionalcommits.org, keepachangelog.com, fastapi.tiangolo.com, docs.sqlalchemy.org, alembic.sqlalchemy.org | raw/*.md | дата проверки 2026-09-03
- 2026-09-03 | update | Заземлены факты по 8 wiki-страницам через пути к файлам и имена функций/классов/маршрутов/тестов | wiki/*.md | 113 тестов подтверждено через `pytest --collect-only`
- 2026-09-03 | gap-found | Зафиксированы пробелы G1–G8 (нет README/CHANGELOG/CI; structlog не используется; нет retry коллизий кода; update без проверки rowcount; нет индекса на expires_at; интеграция-тесты требуют реальную PostgreSQL) | wiki/decisions.md | —
