import logging
from faststream.rabbit import RabbitBroker
from core.config import settings
import os

logger = logging.getLogger(__name__)

# Use env var or construct from settings if not set
rabbitmq_url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

broker = RabbitBroker(rabbitmq_url)
