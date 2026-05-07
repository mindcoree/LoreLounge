"""
RabbitMQ configuration for auth service.
"""

from pydantic import BaseModel, Field


class RabbitmqConfig(BaseModel):
    """RabbitMQ connection settings."""

    url: str = Field(
        default="amqp://guest:guest@localhost:5672/",
        description="RabbitMQ connection URL (amqp://user:password@host:port/)",
    )
    # Отдельные параметры для гибкости конфигурации
    user: str = Field(default="guest", description="RabbitMQ username")
    password: str = Field(default="guest", description="RabbitMQ password")

