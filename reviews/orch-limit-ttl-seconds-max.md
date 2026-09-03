# PR: ограничить ttl_seconds сверху (максимум 86400)

Ветка: `feature/limit-ttl-seconds-max`
Skill: `.agents/skills/orchestrate-coder-reviewer-summarizer.md`
final_gate_council: false (учебный прогон)

## Роли и модели (реальное делегирование)

| Роль | Модель | Механизм |
| --- | --- | --- |
| Orchestrator | `z-ai/glm-5.2` | текущая сессия (гейты, коммит) |
| Coder | `deepseek/deepseek-v4-pro` | `opencode run --model` |
| Reviewer | `moonshotai/kimi-k2.7-code` | `opencode run --model` (read-only) |
| Summarizer | `z-ai/glm-5.2` | текущая сессия (claim ledger) |

## Что сделано

- Введена верхняя граница TTL в `POST /links`: максимум 86400 секунд (сутки).
- При `ttl_seconds > 86400` Pydantic/FastAPI отдаёт 422.
- Дефолт `None` (без expiry) и поведение `ttl_seconds=1` не изменены.
- Добавлены regression-тесты: `86400` → 201, `86401` → 422 (+ БД пуста).

## Изменённые файлы

- `app/api/schemas.py` — константа `MAX_TTL_SECONDS = 86_400`, `le=MAX_TTL_SECONDS` в `Field`.
- `tests/integration/test_links_api.py` — 2 новых теста.

## Проверки (CODE_GATE, гонял Orchestrator)

- `uv run ruff check .` — All checks passed
- `uv run basedpyright` — 0 errors, 0 warnings, 0 notes
- `uv run pytest -q` — 113 passed

## Reviewer (Kimi K2.7)

Вердикт: `MERGE`. Блокирующих: 0. Некритичных: 2 (магические числа 86400/86401 в тестах — рекомендация заменить на `MAX_TTL_SECONDS`/`MAX_TTL_SECONDS+1`; принята как non-blocking, т.к. согласуется со стилем существующих TTL-тестов: `3600`, `1`, `-60`).

## Claim ledger

```json
{
  "decision": "READY_FOR_PR",
  "changes": [
    "Введена верхняя граница TTL в POST /links: максимум 86400 секунд (сутки)",
    "При ttl_seconds > 86400 возвращается 422",
    "Дефолт None (без expiry) и поведение ttl_seconds=1 не изменены",
    "Добавлены regression-тесты: 86400 -> 201, 86401 -> 422 (+ БД пуста)"
  ],
  "claim_ledger": [
    {
      "claim_id": "CLM-001",
      "text": "Введена верхняя граница TTL в POST /links: максимум 86400 секунд (сутки)",
      "evidence_type": "file",
      "evidence_ref": "app/api/schemas.py",
      "evidence_span": "MAX_TTL_SECONDS: int = 86_400",
      "status": "GROUNDED"
    },
    {
      "claim_id": "CLM-002",
      "text": "Введена верхняя граница TTL в POST /links: максимум 86400 секунд (сутки)",
      "evidence_type": "file",
      "evidence_ref": "app/api/schemas.py",
      "evidence_span": "ttl_seconds: int | None = Field(default=None, gt=0, le=MAX_TTL_SECONDS)",
      "status": "GROUNDED"
    },
    {
      "claim_id": "CLM-003",
      "text": "При ttl_seconds > 86400 возвращается 422",
      "evidence_type": "file",
      "evidence_ref": "tests/integration/test_links_api.py",
      "evidence_span": "\"ttl_seconds\": 86401 ... assert resp.status_code == 422",
      "status": "GROUNDED"
    },
    {
      "claim_id": "CLM-004",
      "text": "Дефолт None (без expiry) и поведение ttl_seconds=1 не изменены",
      "evidence_type": "file",
      "evidence_ref": "app/api/schemas.py",
      "evidence_span": "ttl_seconds: int | None = Field(default=None, gt=0, le=MAX_TTL_SECONDS)",
      "status": "GROUNDED"
    },
    {
      "claim_id": "CLM-005",
      "text": "Добавлены regression-тесты: 86400 -> 201, 86401 -> 422 (+ БД пуста)",
      "evidence_type": "file",
      "evidence_ref": "tests/integration/test_links_api.py",
      "evidence_span": "test_post_link_ttl_max_returns_201 ... \"ttl_seconds\": 86400 ... assert resp.status_code == 201",
      "status": "GROUNDED"
    },
    {
      "claim_id": "CLM-006",
      "text": "Добавлены regression-тесты: 86400 -> 201, 86401 -> 422 (+ БД пуста)",
      "evidence_type": "file",
      "evidence_ref": "tests/integration/test_links_api.py",
      "evidence_span": "test_post_link_ttl_over_max_returns_422 ... \"ttl_seconds\": 86401 ... assert resp.status_code == 422 ... assert rows == []",
      "status": "GROUNDED"
    },
    {
      "claim_id": "CLM-007",
      "text": "Проверки: ruff 0, basedpyright 0, pytest 113 passed",
      "evidence_type": "log",
      "evidence_ref": "CODE_GATE (stdout)",
      "evidence_span": "All checks passed! | 0 errors, 0 warnings, 0 notes | 113 passed",
      "status": "GROUNDED"
    }
  ],
  "rework_reason": null
}
```
