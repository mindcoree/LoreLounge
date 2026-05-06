"""Compatibility re-exports for profile config."""


from .database import DatabaseSettings
from .prefixes import ApiProfilePrefix
from .settings import Settings, settings

__all__ = [
	"Settings",
	"settings",
	"DatabaseSettings",
	"ApiProfilePrefix",
]

