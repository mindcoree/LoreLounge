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

class PasswordResetNotification(BaseModel):
    to_email: EmailStr
    reset_link: str

@broker.subscriber("password_reset_queue")
async def handle_password_reset(msg: PasswordResetNotification):
    logger.info(f"Received password reset task for: {msg.to_email}")
    
    subject = "Сброс пароля — LoreLounge"
    body = (
        f"<p>Для сброса пароля перейдите по ссылке:</p>"
        f"<p><a href='{msg.reset_link}'>{msg.reset_link}</a></p>"
        f"<p>Ссылка действительна 30 минут.</p>"
    )
    
    await send_email(
        to_email=msg.to_email,
        subject=subject,
        body=body,
    )
    logger.info("Task completed.")
