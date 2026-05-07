"""
Конфигурация profile через pydantic-settings.

Параметры читаются из env-переменных с префиксом PROFILE_CONFIG__ и
разделителем __ для вложенных секций, например PROFILE_CONFIG__DB__URL.
"""

from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .database import DatabaseSettings
from .prefixes import ApiProfilePrefix
from .minio import MinioSettings

BASE_SERVICE_DIR = Path(__file__).resolve().parents[2]


class RunSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    show_docs: bool = False 


class Settings(BaseSettings):
    """Основные настройки приложения profile."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="PROFILE_CONFIG__",
        env_file=str(BASE_SERVICE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    run: RunSettings = Field(default_factory=RunSettings)
    api: ApiProfilePrefix = Field(default_factory=ApiProfilePrefix)
    db: DatabaseSettings = Field(default_factory=cast(Any, DatabaseSettings))
    minio: MinioSettings = Field(default_factory=cast(Any, MinioSettings))


settings = Settings()


