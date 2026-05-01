from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # RabbitMQ
    rabbitmq_url: str = Field(default="amqp://guest:guest@localhost:5672/")

    # SMTP Settings
    smtp_host: str = Field(...)
    smtp_port: int = Field(...)
    smtp_user: str = Field(...)
    smtp_password: str = Field(...)
    smtp_tls: bool = Field(default=True)
    smtp_from: str = Field(...)

settings = Settings()
