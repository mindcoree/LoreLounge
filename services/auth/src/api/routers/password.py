from fastapi import APIRouter
import logging

from uuid import UUID
from api.dependencies.service import AuthServiceDep
from api.dependencies.auth import PayloadEntity
from api.schemas.password import (
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
    PasswordResetCheckResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
)

router = APIRouter(tags=["Password"])
logger = logging.getLogger(__name__)

@router.get(
    "/password-reset-check",
    response_model=PasswordResetCheckResponse,
    summary="Проверка токена сброса пароля",
)
async def password_reset_check(
    token: str,
    service: AuthServiceDep,
) -> PasswordResetCheckResponse:
    """Проверяет валидность токена и возвращает время истечения."""
    return await service.password_reset_check(token)

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

@router.post(
    "/password-change",
    response_model=PasswordChangeResponse,
    summary="Изменение пароля",
)
async def password_change(
    payload: PayloadEntity,
    data: PasswordChangeRequest,
    service: AuthServiceDep,
) -> PasswordChangeResponse:
    """Изменяет пароль авторизованного пользователя после проверки текущего пароля."""
    return await service.change_password(entity_id=UUID(payload.sub), data=data)
