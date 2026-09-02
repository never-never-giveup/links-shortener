from __future__ import annotations

import random
import string

from locust import HttpUser, between, task

# Сценарий FastAPI-трека: смесь записи и чтения.

# Длина случайного суффикса в URL-адресах, генерируемых для нагрузки.
_URL_SUFFIX_LENGTH = 8
# Верхний лимит кэша коротких кодов в одном виртуальном пользователе:
# без него _codes растёт без ограничения, раздувая random.choice() на поздних итерациях.
_CODES_CACHE_LIMIT = 200
# Пауза между запросами одного виртуального пользователя (секунды).
_WAIT_MIN = 0.0
_WAIT_MAX = 0.05
# Веса задач locust — пропорция запись:чтение-по-коду:листинг = 3:6:1.
# Чтение доминирует, как в реальном трафике сокращателя ссылок.
_CREATE_WEIGHT = 3
_GET_WEIGHT = 6
_LIST_WEIGHT = 1


def _random_url() -> str:
    suffix = "".join(random.choices(string.ascii_lowercase, k=_URL_SUFFIX_LENGTH))
    return f"https://example.com/{suffix}"


class LinkUser(HttpUser):
    """Виртуальный пользователь сокращателя ссылок.

    Эмулирует смесь записи и чтения: создаёт новые ссылки, переходит по
    коротким кодам и периодически запрашивает список. Коды успешных POST
    кэшируются в ``_codes`` для последующих GET ``/links/{code}``.
    """

    wait_time = between(_WAIT_MIN, _WAIT_MAX)

    def on_start(self) -> None:
        """Инициализация кэша коротких кодов при старте виртуального пользователя."""
        self._codes: list[str] = []

    @task(_CREATE_WEIGHT)
    def create_link(self) -> None:
        """Создаёт новую короткую ссылку и кэширует её код для последующего чтения."""
        resp = self.client.post("/links", json={"url": _random_url()})
        if resp.status_code == 201:
            code = resp.json().get("short_code")
            if code and len(self._codes) < _CODES_CACHE_LIMIT:
                self._codes.append(code)

    @task(_GET_WEIGHT)
    def get_link(self) -> None:
        """Переходит по случайному кэшированному короткому коду (read-heavy путь)."""
        if not self._codes:
            return
        code = random.choice(self._codes)
        self.client.get(f"/links/{code}", name="/links/{code}")

    @task(_LIST_WEIGHT)
    def list_links(self) -> None:
        """Запрашивает список всех ссылок (самый редкий сценарий)."""
        self.client.get("/links")
