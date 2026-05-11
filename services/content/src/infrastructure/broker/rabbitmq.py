from faststream.rabbit import RabbitBroker

from config.settings import settings


broker = RabbitBroker(settings.rabbitmq.url)
