"""
Конфигурация auth-service через pydantic-settings.

Все параметры читаются из env-переменных с префиксом CONFIG__ и
разделителем __ для вложенных моделей (например CONFIG__DB__URL).
"""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_SERVICE_DIR = Path(__file__).parent.parent.parent


class RunConfig(BaseModel):
    port: int = 8000
    host: str = "0.0.0.0"


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 20
    max_overflow: int = 10
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class AuthJWT(BaseModel):
    private_key: Path = BASE_SERVICE_DIR / "certs" / "private_key.pem"
    public_key: Path = BASE_SERVICE_DIR / "certs" / "public_key.pem"
    algorithm: str = "RS256"
    access_expire_min: int = 15
    refresh_expire_days: int = 7


class SMTPConfig(BaseModel):
    """Настройки SMTP (опциональны — email-отправка пропускается, если не задан)."""

    host: str = ""
    port: int = 587
    user: str = ""
    password: str = ""
    from_email: str = ""
    use_tls: bool = True
    use_ssl: bool = False


class S3Config(BaseModel):
    """Настройки S3/MinIO (опциональны)."""

    host: str = ""
    port: int = 9000
    access_key: str = ""
    secret_key: str = ""
    bucket: str = "lorelounge"

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"

    @property
    def secure(self) -> bool:
        return False


class CORSConfig(BaseModel):
    origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:80",
        "http://localhost",
        "http://frontend:3000",
        "http://127.0.0.1:3000",
    ]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="CONFIG__",
        env_file=".env",
        extra="ignore",
    )

    run: RunConfig = RunConfig()
    db: DatabaseConfig
    auth: AuthJWT = AuthJWT()
    smtp: SMTPConfig = SMTPConfig()
    s3: S3Config = S3Config()
    cors: CORSConfig = CORSConfig()

    # URL фронтенда для формирования ссылок (password-reset и т.д.)
    frontend_url: str = "http://localhost:3000"


settings = Settings()
