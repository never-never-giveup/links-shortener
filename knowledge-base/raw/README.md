# raw/ — неизменяемые внешние первоисточники

Слой `raw/` хранит **ссылки на внешние первоисточники**, на которые опирается
`wiki/`. Каждая карточка фиксирует: источник, URL, дату проверки и какие
именно факты вики из него берутся.

## Правила слоя

- **Не копируем** сюда содержимое внешних документов целиком (авторские права).
  Храним URL + дату проверки + выжимку проверенного факта.
- Карточка **неизменяема постфактум**: если внешний источник меняется, создаётся
  новая карточка с новой датой, старая остаётся для истории (append-only по
  аналогии с `LOG.md`).
- Внешний факт в `wiki/` обязан ссылаться на карточку из `raw/` (URL + дата
  проверки) — см. `../AGENTS.md`, операция `ingest`.

## Реестр карточек

| Карточка | Источник | Дата проверки |
|---|---|---|
| [llm-wiki.md](llm-wiki.md) | gist.github.com/karpathy | 2026-09-03 |
| [conventional-commits.md](conventional-commits.md) | conventionalcommits.org | 2026-09-03 |
| [keep-a-changelog.md](keep-a-changelog.md) | keepachangelog.com | 2026-09-03 |
| [fastapi.md](fastapi.md) | fastapi.tiangolo.com | 2026-09-03 |
| [sqlalchemy.md](sqlalchemy.md) | docs.sqlalchemy.org | 2026-09-03 |
| [alembic.md](alembic.md) | alembic.sqlalchemy.org | 2026-09-03 |
