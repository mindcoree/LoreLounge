"""Compatibility re-exports for profile config."""

from .cors import CORSSettings
from .database import DatabaseSettings
from .prefixes import ApiPrefix, ApiUsersPrefix
from .settings import Settings, settings

__all__ = [
	"Settings",
	"settings",
	"DatabaseSettings",
	"CORSSettings",
	"ApiPrefix",
	"ApiUsersPrefix",
]

