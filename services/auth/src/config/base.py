"""Compatibility re-exports for auth config."""

from .database import DatabaseSettings
from .jwt import AuthJWT
from .prefixes import ApiAuthPrefix
from .settings import Settings, settings

__all__ = [
    "Settings",
    "settings",
    "DatabaseSettings",
    "AuthJWT",
    "ApiAuthPrefix",
]
