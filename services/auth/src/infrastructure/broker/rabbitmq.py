import logging
from faststream.rabbit import RabbitBroker
from core.config import settings
import os
from domain.common.interfaces import AbstractMessageBroker
from typing import Any

logger = logging.getLogger(__name__)

# Use env var or construct from settings if not set
rabbitmq_url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

class RabbitMQAdapter(AbstractMessageBroker):
    def __init__(self, url: str):
        self.broker = RabbitBroker(url)

    async def connect(self):
        await self.broker.connect()

    async def disconnect(self):
        await self.broker.close()

    async def publish(self, message: Any, queue: str) -> None:
        await self.broker.publish(message, queue=queue)

# If we still want a global broker instance for app startup/shutdown
broker = RabbitBroker(rabbitmq_url)
