"""
Слой сервисов для auth.

AuthServices         — регистрация, вход, refresh, payload, сброс пароля.
"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID
from typing import Optional, Dict

from jwt.exceptions import InvalidTokenError # type: ignore

from core import security as auth
from core.config import settings
from core.types import TOKEN_TYPE_FIELD, REFRESH_TOKEN_TYPE
from domain.common.enums import Role
from domain.entity.repository import AbstractAuthRepository
from domain.common.interfaces import AbstractMessageBroker
from domain.role_requests.repository import RoleRequestRepository
from domain.common.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    TokenExpiredError,
    UserNotFoundError,
    GatewayAuthenticationRequiredError,
    PasswordsDoNotMatchError,
    InvalidOrExpiredResetTokenError,
    ResetTokenAlreadyUsedError
)
from domain.entity.schemas import (
    AccessTokenPayload,
    AuthEntityIn,
    AuthCredentials,
    AuthEntitySchema,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
    DomainAuthEntity,
    PasswordResetNotification
)

logger = logging.getLogger(__name__)


class AuthServices:
    """Сервисный слой для логики аутентификации."""

    def __init__(
        self,
        repository: AbstractAuthRepository,
        message_broker: AbstractMessageBroker,
        role_request_repo: Optional[RoleRequestRepository] = None,
    ) -> None:
        self.repo = repository
        self.message_broker = message_broker
        self.role_request_repo = role_request_repo

    async def register_entity(self, auth_in: AuthEntityIn) -> DomainAuthEntity:
        """Регистрирует нового пользователя."""
        logger.info("Начало регистрации для %s (запрошенная роль: %s)", auth_in.email, auth_in.role)

        hashed_password = await auth.hash_password(auth_in.password)
        entity_data = {
            "email": auth_in.email,
            "hash_password": hashed_password,
            "role": Role.READER,
        }

        entity = await self.repo.create_entity(entity_data)

        logger.info("Пользователь создан: id=%s", entity.id)

        desired_role = auth_in.role
        if desired_role and desired_role.value != Role.READER.value and self.role_request_repo:
            await self.role_request_repo.create(
                entity_id=entity.id, requested_role=desired_role
            )
            logger.info("Создана заявка на роль %s для entity_id=%s", desired_role, entity.id)

        return entity

    async def authenticate_entity(self, credentials: AuthCredentials) -> DomainAuthEntity:
        """Проверяет email + пароль и возвращает AuthEntity."""
        entity = await self.repo.get_auth_entity_by_email(email=credentials.email)

        if not entity or not await auth.verify_password(
            password=credentials.password,
            hashed_password=entity.hash_password,
        ):
            raise InvalidCredentialsError("Неверный email или пароль")

        logger.info("Успешный вход: id=%s role=%s", entity.id, entity.role)
        return entity

    async def refresh_authentication(
        self,
        refresh_token: str,
    ) -> Dict[str, str]:
        """Обновляет access-токен по refresh-токену."""
        try:
            refresh_payload = await auth.decode_jwt(token=refresh_token)
        except InvalidTokenError:
            raise TokenExpiredError("Refresh-токен невалиден или просрочен")

        token_type = refresh_payload.get(TOKEN_TYPE_FIELD)
        if token_type != REFRESH_TOKEN_TYPE:
            raise TokenExpiredError(f"Ожидался refresh-токен, получен: {token_type}")

        entity_id = UUID(refresh_payload.get("sub"))
        entity = await self.repo.get_auth_entity_by_id(entity_id)
        if not entity:
            raise UserNotFoundError("Пользователь не найден")

        auth_payload = AuthEntitySchema(
            id=entity.id,
            role=entity.role,
            email=entity.email,
        )
        access_token = await auth.create_access_token(auth_info=auth_payload)
        return {"access_token": access_token}

    async def access_token_payload(self, headers: dict) -> AccessTokenPayload:
        """Извлекает payload. Приоритет — заголовки от KrakenD Gateway."""
        user_id = headers.get("x-user-id")
        user_role = headers.get("x-user-role")
        user_email = headers.get("x-user-email")

        if user_id and user_role:
            return AccessTokenPayload(
                sub=str(user_id),
                role=Role(user_role),
                email=user_email or ""
            )

        raise GatewayAuthenticationRequiredError("Требуется аутентификация через Gateway")

    async def password_reset_request(
        self, data: PasswordResetRequest
    ) -> PasswordResetResponse:
        """Генерирует ссылку для сброса пароля."""
        email = str(data.email)
        generic_response = PasswordResetResponse(
            detail="Если email зарегистрирован, инструкция отправлена."
        )

        try:
            entity = await self.repo.get_auth_entity_by_email(email)
        except Exception:
            logger.exception("Ошибка поиска пользователя по email=%s", email)
            return PasswordResetResponse(detail="Внутренняя ошибка. Попробуйте позже.")

        if not entity:
            return generic_response

        try:
            await self.repo.cleanup_reset_tokens(datetime.now(timezone.utc))
            await self.repo.invalidate_reset_tokens(entity.id)
            
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
            await self.repo.create_reset_token(entity.id, token_hash, expires_at)

            reset_link = f"{settings.frontend_url}/reset-password?token={token}"
            
            message = PasswordResetNotification(
                to_email=entity.email,
                reset_link=reset_link,
            )
            await self.message_broker.publish(message, queue="password_reset_queue")
            
            return generic_response
        except Exception:
            logger.exception("Ошибка генерации токена сброса пароля для email=%s", email)
            return PasswordResetResponse(detail="Внутренняя ошибка. Попробуйте позже.")

    async def password_reset_confirm(self, data: PasswordResetConfirm) -> PasswordResetResponse:
        if data.new_password != data.repeat_password:
            raise PasswordsDoNotMatchError("Пароли не совпадают")

        token_hash = hashlib.sha256(data.token.encode("utf-8")).hexdigest()
        reset_token = await self.repo.get_reset_token_by_hash(token_hash)

        if not reset_token:
            raise InvalidOrExpiredResetTokenError("Некорректный или просроченный токен")

        if reset_token.used:
            raise ResetTokenAlreadyUsedError("Токен уже использован")

        now = datetime.now(timezone.utc)
        if reset_token.expires_at < now - timedelta(seconds=10):
            raise InvalidOrExpiredResetTokenError("Некорректный или просроченный токен")

        entity = await self.repo.get_auth_entity_by_id(reset_token.entity_id)
        if not entity:
            raise UserNotFoundError("Пользователь не найден")

        new_hash = await auth.hash_password(data.new_password)
        await self.repo.update_password(reset_token.entity_id, new_hash)
        await self.repo.mark_reset_token_used(reset_token.id)
        return PasswordResetResponse(detail="Пароль успешно изменён")

    async def get_entity_by_id(self, entity_id: UUID) -> DomainAuthEntity | None:
        return await self.repo.get_auth_entity_by_id(entity_id)