import logging
from faststream.rabbit import RabbitBroker
from core.config import settings
from domain.common.interfaces import AbstractMessageBroker
from typing import Any

logger = logging.getLogger(__name__)


class RabbitMQAdapter(AbstractMessageBroker):
    def __init__(self, url: str):
        self.broker = RabbitBroker(url)

    async def connect(self):
        await self.broker.connect()

    async def disconnect(self):
        await self.broker.close()

    async def publish(self, message: Any, queue: str) -> None:
        await self.broker.publish(message, queue=queue)


# Use settings.rabbitmq.url for the broker
broker = RabbitBroker(settings.rabbitmq.url)
