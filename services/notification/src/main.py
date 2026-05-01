import logging
from faststream import FastStream
from core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

from infrastructure.broker.rabbitmq import broker
from domain.notification.schemas import PasswordResetNotification
from infrastructure.email.smtp import send_email

app = FastStream(broker)

@broker.subscriber("password_reset_queue")
async def handle_password_reset(msg: PasswordResetNotification):
    logger.info(f"Received password reset task for: {msg.to_email}")
    
    subject = "Сброс пароля — LoreLounge"
    body = (
        f"<p>Для сброса пароля перейдите по ссылке:</p>"
        f"<p><a href='{msg.reset_link}'>Сбросить пароль</a></p>"
        f"<p>Ссылка действительна 30 минут.</p>"
    )
    
    await send_email(
        to_email=msg.to_email,
        subject=subject,
        body=body,
    )
    logger.info("Task completed.")
