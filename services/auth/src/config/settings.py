"""
Конфигурация auth через pydantic-settings.

Параметры читаются из env-переменных с префиксом AUTH__ и
разделителем __ для вложенных секций, например AUTH__DB__POSTGRES_USER.
"""

from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .database import DatabaseSettings
from .jwt import AuthJWT
from .prefixes import ApiAuthPrefix
from .rabbitmq import RabbitmqSettings
from .redis import RedisSettings

BASE_SERVICE_DIR = Path(__file__).resolve().parents[2]


class RunSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    show_docs: bool = False


class Settings(BaseSettings):
    """Основные настройки приложения auth."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="AUTH__",
        env_file=str(BASE_SERVICE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    run: RunSettings = Field(default_factory=RunSettings)
    api: ApiAuthPrefix = Field(default_factory=ApiAuthPrefix)
    db: DatabaseSettings = Field(default_factory=cast(Any, DatabaseSettings))
    auth: AuthJWT = Field(default_factory=AuthJWT)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    rabbitmq: RabbitmqSettings = Field(default_factory=cast(Any, RabbitmqSettings))

    # URL фронтенда для формирования ссылок (password-reset и т.д.)
    frontend_url: str = "http://localhost:3000"


settings = Settings()
