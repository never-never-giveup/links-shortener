# Model Battle: unit tests for LinkService

## Object ID участников (до и после ревью)

| Ветка | Object ID (до) | Object ID (после) | Совпадение |
|---|---|---|---|
| workshop/unit-tests-glm | f62b806261a34fa62298f96e37ec9cbb211563d5 | f62b806261a34fa62298f96e37ec9cbb211563d5 | ✅ |
| workshop/unit-tests-qwen | 3362f474c3c8a43f96695ab84cfc10828a81821b | 3362f474c3c8a43f96695ab84cfc10828a81821b | ✅ |

## Таблица проверок

| Проверка | workshop/unit-tests-glm | workshop/unit-tests-qwen |
|---|---|---|
| Ruff | ✅ All checks passed | ✅ All checks passed |
| BasedPyright | ✅ 0 errors | ❌ 4 errors (строки 183, 202 — доступ к `_store` через `LinkRepositoryProtocol`) |
| pytest unit | ✅ 17 passed | ✅ 16 passed |
| branch coverage LinkService | ✅ 100% | ✅ 100% |
| Fake соответствует реальному `LinkRepositoryProtocol` | ✅ | ❌ |

## Сильные стороны

### workshop/unit-tests-glm
- `FakeLinkRepository` полностью повторяет async-контракт реального репозитория, не поднимает лишних исключений.
- Фабрика `make_service()` возвращает кортеж `(service, repo)`, что позволяет готовить состояние через публичный API Fake, не ломая инкапсуляцию.
- Для expired/disabled сценариев используется `repo.add(...)`, а не прямое мутирование `_store`.
- Покрыты граничные случаи: `ttl_seconds=0`, отрицательный TTL, пустой список ссылок, limit.
- Нет `# type: ignore`, нет прямого доступа к приватным полям.
- Все статические и runtime-проверки зелёные.

### workshop/unit-tests-qwen
- Есть docstring у каждого теста.
- Проверяет пустой URL и `resolve` несуществующей ссылки явно.
- `expires_at` сверяется точным равенством с `created_at + ttl`, что даёт более сильный assert по сравнению с нестрогим неравенством.

## Слабые стороны и дефекты

### workshop/unit-tests-glm
- `FakeLinkRepository.list_all` не воспроизводит сортировку реального репозитория (`order_by(LinkModel.id.desc())`). В текущих тестах это не критично, но при добавлении asserts на порядок даст ложную уверенность.
- Нет отдельного теста на `resolve` несуществующего кода (покрыто косвенно через `test_get_link_nonexistent_raises`).

### workshop/unit-tests-qwen
- **Блокирующий:** BasedPyright падает с 4 ошибками в строках 183 и 202: `service._repository._store` с `# type: ignore`. Доступ к приватному состоянию Fake через поле `_repository` нарушает инкапсуляцию и type safety.
- **Контракт Fake:** `FakeLinkRepository.add` поднимает `ShortCodeTakenError`, которого не делает реальный `LinkRepository`. Это означает, что Fake ведёт себя иначе, чем production-репозиторий, и может скрыть или создать регрессию.
- **Контракт Fake:** `FakeLinkRepository.update` поднимает `LinkNotFoundError`, которого не делает реальный `LinkRepository` (он выполняет UPDATE без проверки).
- Тесты expired/disabled сценариев мутируют `repo._store` напрямую, минуя API репозитория, что снижает изоляцию и читаемость.
- Нет теста на пустой `list_links`.
- `make_service()` не возвращает репозиторий, что вынуждает тесты использовать `service._repository`.

## Решение

workshop/unit-tests-glm проходит все гейты, имеет более точный Fake, лучшую изоляцию и не нарушает type safety. workshop/unit-tests-qwen падает на BasedPyright и содержит отклонения от реального контракта репозитория.

WINNER=workshop/unit-tests-glm
