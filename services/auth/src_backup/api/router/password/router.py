from fastapi import APIRouter
import logging

from ..auth.dependencies import AuthServiceDep
from domain.entity.schemas import (
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/password-reset-request",
    response_model=PasswordResetResponse,
    summary="Запрос на сброс пароля",
)
async def password_reset_request(
    data: PasswordResetRequest,
    service: AuthServiceDep,
) -> PasswordResetResponse:
    """Генерирует ссылку для сброса пароля и публикует сообщение в RabbitMQ."""
    return await service.password_reset_request(data)

@router.post(
    "/password-reset-confirm",
    response_model=PasswordResetResponse,
    summary="Подтверждение нового пароля",
)
async def password_reset_confirm(
    data: PasswordResetConfirm,
    service: AuthServiceDep,
) -> PasswordResetResponse:
    """Принимает токен + новый пароль и обновляет хеш в БД."""
    return await service.password_reset_confirm(data)
