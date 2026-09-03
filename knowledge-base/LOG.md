# LOG — журнал событий базы знаний

Append-only. Свежее событие — сверху. Формат записи:
`ГГГГ-ММ-ДД | <тип> | <что> | <где> | <контекст>`.

- 2026-09-03 | ingest | Первоначальная сборка базы знаний: raw/ (6 карточек внешних источников) + wiki/ (8 страниц) + AGENTS.md + INDEX.md + LOG.md | knowledge-base/ | ветка workshop/project-knowledge-base, off main; код приложения не изменялся
- 2026-09-03 | ingest | Зафиксированы внешние первоисточники: conventionalcommits.org, keepachangelog.com, fastapi.tiangolo.com, docs.sqlalchemy.org, alembic.sqlalchemy.org | raw/*.md | дата проверки 2026-09-03
- 2026-09-03 | update | Заземлены факты по 8 wiki-страницам через пути к файлам и имена функций/классов/маршрутов/тестов | wiki/*.md | 113 тестов подтверждено через `pytest --collect-only`
- 2026-09-03 | gap-found | Зафиксированы пробелы G1–G8 (нет README/CHANGELOG/CI; structlog не используется; нет retry коллизий кода; update без проверки rowcount; нет индекса на expires_at; интеграция-тесты требуют реальную PostgreSQL) | wiki/decisions.md | —
