import logging
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from pydantic import BaseModel, EmailStr

from core.config import settings
from services.email import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

broker = RabbitBroker(settings.rabbitmq_url)
app = FastStream(broker)

class EmailNotificationSchema(BaseModel):
    to_email: EmailStr
    subject: str
    body: str

@broker.subscriber("email_notifications_queue")
async def handle_email_notification(msg: EmailNotificationSchema):
    logger.info(f"Received email notification task for: {msg.to_email}")
    await send_email(
        to_email=msg.to_email,
        subject=msg.subject,
        body=msg.body,
    )
    logger.info("Task completed.")
