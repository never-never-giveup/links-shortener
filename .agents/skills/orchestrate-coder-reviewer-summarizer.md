# Skill: Оркестрация Coder → Reviewer → Summarizer

Здесь — учебный профиль AgentPlatform (компактный).

## Роли и модели (AgentPlatform pins уже в opencode.json)

| Роль | Кто | Модель (id для `--model` / UI) | Права | Skill роли |
| --- | --- | --- | --- | --- |
| Orchestrator | владелец состояния | `z-ai/glm-5.2` (текущая сессия) | гейты, итерации, стоп | этот файл |
| Coder (Разработчик) | **пишет код** + тесты | `deepseek/deepseek-v4-pro` | edit + bash в проекте | `.agents/skills/feature.md` (или bugfix/refactor) |
| Reviewer (Ревьювер) | **ревью** / вердикт | `moonshotai/kimi-k2.7-code` | **read-only** | `.agents/skills/code-review.md` |
| Summarizer (Сводка) | PR-отчёт + claim ledger | `z-ai/glm-5.2` | **read-only** | гейт tests-* + отчёт |

В OpenCode предпочтительно отдельные проходы: `opencode run --model agentplatform/<id> "…"`. В одном TUI — переключай модель между ролями, не смешивай роли в одном ответе. Continue: новый чат + смена модели на каждую роль; Orchestrator-сессия только координирует (или ты сам по шагам skill).

## Нерушимые правила

1. Один владелец состояния — Orchestrator (считает итерации, гоняет гейты, решает стоп).
2. Код меняет только Coder. Reviewer/Summarizer — read-only; любое изменение worktree ими = стоп.
3. Не верь самоотчёту: Orchestrator сам гоняет команды и читает stdout.
4. Summarizer только после `MERGE`. Красный CODE_GATE / `CHANGES_REQUESTED` → назад к Coder.
5. Бюджеты возвратов (по умолчанию **5** на контур, считает Orchestrator):
   - CODE_GATE → Coder ≤ **5**
   - Reviewer → Coder (`CHANGES_REQUESTED`) ≤ **5**
   - Summarizer → Coder (`REWORK`) ≤ **5** Summarizer не «украшает MERGE»: ведёт **claim ledger**, ловит галлюцинации и пустые придирки Reviewer; при сомнении — `REWORK`, не слепой `READY_FOR_PR`.
6. `git push` / открытие PR — не делать (отдельный шаг человека).
7. Opt-in совет на FINAL_GATE (`critical` / `final_gate_council`) — **только если явно в задаче**; по умолчанию в учебной практике **выключен**.

## Конечный автомат

```
INIT → CODER → CODE_GATE ─┬─ fail → CODER          (бюджет ≤5)
                          └─ pass → REVIEWER
                                    ├─ CHANGES_REQUESTED → CODER  (бюджет ≤5)
                                    ├─ BLOCKED → ESCALATE
                                    └─ MERGE → SUMMARIZER
                                               ├─ REWORK → CODER  (бюджет ≤5)
                                               ├─ BLOCKED → ESCALATE
                                               └─ READY_FOR_PR
                                                  └─ (opt) council 2/3 по claims
```

## CODE_GATE (гоняет Orchestrator)

```
uv run ruff check .
uv run basedpyright
uv run pytest -q
```

Красный → Coder с конкретным логом (не в Reviewer), пока бюджет CODE_GATE→Coder ≤5 не исчерпан. Не ослаблять гейт/coverage.

## Handoff (компактно, без рассуждений)

Coder → `{"changed":[...],"commands":[{"cmd":"...","exit":0}],"risks":[...]}` Reviewer → одна строка вердикта `MERGE|CHANGES_REQUESTED|BLOCKED` + findings `file:line` (`CONFIRMED` только с дословным evidence). Summarizer → `READY_FOR_PR` | `REWORK` | `BLOCKED` + **claim_ledger** (обязателен):

```json
{
  "decision": "READY_FOR_PR",
  "changes": ["API отдаёт 410 на LinkExpired"],
  "claim_ledger": [{
    "claim_id": "CLM-001",
    "text": "API отдаёт 410 на LinkExpired",
    "evidence_type": "file",
    "evidence_ref": "app/api/routes.py",
    "evidence_span": "status_code=410",
    "status": "GROUNDED"
  }],
  "rework_reason": null
}
```

Правила ledger (учебный минимум):

- каждый bullet из `changes[]` = `claim_ledger[].text` дословно;
- `READY_FOR_PR` только если все claims `GROUNDED` и `evidence_span` есть в файле/логе;
- иначе `decision=REWORK` + непустой `rework_reason` (не «красивый PR»);
- артефакт при READY: `reviews/orch-<slug>.md` (PR-текст с секцией ledger).

## FINAL_GATE (Orchestrator)

1. Reviewer = `MERGE`; CODE_GATE зелёный после последней правки.
2. Summarizer read-only (worktree не менялся).
3. У каждого claim span реально лежит в `evidence_ref` (открой файл и сверь).
4. Opt-in council: только если в задаче явно `critical=true` или `final_gate_council=true` — тогда тройка моделей (как в panel-backends quality) голосует majority 2/3 **по каждому claim_id** (`CONFIRMED|REJECT|INCONCLUSIVE`); ≥2 REJECT → `REWORK`. Без флага — совет **не** запускать.
5. `git push` / PR — человек.

## Как запускать (участник)

1. `cd ~/work/ai-python-workshop/fastapi`
2. Агент (GLM 5.2 = Orchestrator) читает **этот** skill.
3. Задача — одна строка (feature/bugfix); для учебной практики council не включать.
4. Orchestrator ведёт цикл; роли на своих моделях (DeepSeek V4 / Kimi 2.7 / GLM 5.2).
5. Ты подключаешься на `BLOCKED` или `READY_FOR_PR` (с claim ledger в отчёте).

## Stop

Исчерпан бюджет любого контура (≤5); тот же блокер два раунда; read-only изменил код; Coder ослабил тест/гейт; claim без span пытаются сдать как READY; нужно продуктовое решение человека. Сохранить diff+вердикт+ledger и назвать следующий шаг.
