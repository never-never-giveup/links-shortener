from __future__ import annotations

import secrets

from app.domain.value_objects import CODE_ALPHABET, DEFAULT_CODE_LENGTH, ShortCode


def generate_short_code(code_length: int = DEFAULT_CODE_LENGTH) -> ShortCode:
    """Генерирует случайный короткий код из [A-Za-z0-9] заданной длины."""
    return ShortCode("".join(secrets.choice(CODE_ALPHABET) for _ in range(code_length)))
