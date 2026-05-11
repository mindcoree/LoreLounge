""" Compatibility re-exports for content config. """

from .database import DatabaseSettings
from .prefixes import ApiContentPrefix
from .storage import MinioSettings, StorageSettings

__all__ = [
    "DatabaseSettings",
    "MinioSettings",
    "StorageSettings",
    "ApiContentPrefix",
]