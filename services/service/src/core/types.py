"""
Константы для работы с JWT в auth-service.
"""

from typing import Annotated

from sqlalchemy import JSON as _JSON
from sqlalchemy.orm import mapped_column

# ── JWT type field ────────────────────────────────────────────────────────────

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

# ── Cookie keys ───────────────────────────────────────────────────────────────

ACCESS_TOKEN_COOKIE_KEY = "access_token"
REFRESH_TOKEN_COOKIE_KEY = "refresh_token"

# ── SQLAlchemy type aliases ───────────────────────────────────────────────────

JSON = Annotated[dict, mapped_column(_JSON)]
