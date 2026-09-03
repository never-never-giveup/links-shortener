# External source: FastAPI

- **URL:** https://fastapi.tiangolo.com/
- **Дата проверки:** 2026-09-03
- **Тип:** документация веб-фреймворка

## Что берёт вики

Проект построен на FastAPI. Зависимость зафиксирована во внутреннем первоисточнике
`pyproject.toml`: `fastapi[standard]>=0.137.0`. Используемые механизмы FastAPI,
подтверждённые кодом:

- `FastAPI(title=...)` и `application.include_router(router)` — `app/main.py:23-25`,
  функция `create_app`.
- `APIRouter(prefix="/links", tags=["links"])` — `app/api/routes.py:10`.
- Зависимости через `Annotated[..., Depends(...)]` — `app/api/deps.py:16,23`.
- `RedirectResponse(url=..., status_code=HTTP_307_TEMPORARY_REDIRECT)` —
  `app/main.py:17-18`, функция `redirect_to_target`.
- Маппинг доменных ошибок в `HTTPException` — `app/api/errors.py:27-30`,
  функция `raise_for_domain_error`.
- Pydantic-схемы запросов/ответов с `Field(..., gt=0, le=...)` —
  `app/api/schemas.py:10-24`.

## Факты, подтверждённые внешним источником

- Валидация входных данных выполняется Pydantic через декларативные модели;
  нарушение ограничений `Field` → HTTP 422 (поведение FastAPI/Pydantic).
