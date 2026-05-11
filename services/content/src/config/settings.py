"""
Configurations content through pydantic-settings.

Parameters are read from env variables with the PROFILE_CONFIG__ prefix
and a __ separator for nested sections, for example, PROFILE_CONFIG__DB__URL.
"""

from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .database import DatabaseSettings
from .rabbitmq import RabbitmqSettings
from .prefixes import ApiContentPrefix
from .storage import MinioSettings, StorageSettings

BASE_SERVICE_DIR = Path(__file__).resolve().parents[2]


class RunSettings(BaseModel):
    """Settings related to running the application."""

    host: str = "0.0.0.0"
    port: int = 8000
    show_docs: bool = True


class Settings(BaseSettings):
    """Main settings class."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="CONTENT__",
        env_file=str(BASE_SERVICE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    run: RunSettings = Field(default_factory=RunSettings)
    api: ApiContentPrefix = Field(default_factory=ApiContentPrefix)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    db: DatabaseSettings = Field(cast(Any, default_factory=DatabaseSettings))
    minio: MinioSettings = Field(cast(Any, default_factory=MinioSettings))
    rabbitmq: RabbitmqSettings = Field(cast(Any, default_factory=RabbitmqSettings))


settings = Settings()
