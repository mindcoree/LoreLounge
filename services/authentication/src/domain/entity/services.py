"""
Слой сервисов для auth-service.

AuthServices         — регистрация, вход, refresh, payload, сброс пароля.
RoleRequestService   — управление заявками на смену роли.
"""

import logging
from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status, Response, Request
from jwt.exceptions import InvalidTokenError
from sqlalchemy.exc import IntegrityError

from core import security as auth
from core.config import settings
from core.types import TOKEN_TYPE_FIELD, REFRESH_TOKEN_TYPE, ACCESS_TOKEN_COOKIE_KEY, REFRESH_TOKEN_COOKIE_KEY
from domain.common.enums import Role, DesiredRole, RoleRequestStatus
from domain.entity.repository import AuthRepository, RoleRequestRepository
from domain.entity.schemas import (
    AccessTokenPayload,
    AuthEntityIn,
    AuthCredentials,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
    RoleRequestCreate,
)
from infrastructure.db.models import AuthEntity, RoleRequest

logger = logging.getLogger(__name__)


class AuthServices:
    """Сервисный слой для логики аутентификации."""

    def __init__(
        self,
        repository: AuthRepository,
        role_request_repo: Optional[RoleRequestRepository] = None,
    ) -> None:
        self.repo = repository
        self.role_request_repo = role_request_repo

    # ── Регистрация ──────────────────────────────────────────────────────────

    async def register_entity(self, auth_in: AuthEntityIn) -> AuthEntity:
        """
        Регистрирует нового пользователя.

        Если запрошена роль ≠ READER, создаётся pending-заявка, а сам
        пользователь получает базовую роль READER.
        """
        logger.info("Начало регистрации для %s (запрошенная роль: %s)", auth_in.email, auth_in.role)

        hashed_password = await auth.hash_password(auth_in.password)
        entity_data = {
            "email": auth_in.email,
            "login": auth_in.login,
            "hash_password": hashed_password,
            "role": Role.READER,
        }

        try:
            entity = await self.repo.create_entity(entity_data)
        except IntegrityError:
            logger.warning("Пользователь с email=%s уже существует", auth_in.email)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email или логином уже существует",
            )

        logger.info("Пользователь создан: id=%s", entity.id)

        # Заявка на роль, если запрошена не READER
        desired_role = auth_in.role
        if desired_role and desired_role.value != Role.READER.value and self.role_request_repo:
            await self.role_request_repo.create(
                entity_id=entity.id, requested_role=desired_role
            )
            logger.info("Создана заявка на роль %s для entity_id=%s", desired_role, entity.id)

        return entity

    # ── Аутентификация ───────────────────────────────────────────────────────

    async def authenticate_entity(self, credentials: AuthCredentials) -> AuthEntity:
        """Проверяет email + пароль и возвращает AuthEntity."""
        entity = await self.repo.get_auth_entity_by_email(email=credentials.email)

        if not entity or not await auth.verify_password(
            password=credentials.password,
            hashed_password=entity.hash_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
            )

        logger.info("Успешный вход: id=%s role=%s", entity.id, entity.role)
        return entity

    # ── Refresh ──────────────────────────────────────────────────────────────

    async def refresh_authentication(
        self,
        response: Response,
        refresh_token: str,
    ) -> AuthEntity:
        """
        Обновляет access-токен по refresh-токену.

        Декодирует refresh-токен → проверяет тип → ищет пользователя →
        выдаёт новый access-токен в cookie.
        """
        try:
            refresh_payload = await auth.decode_jwt(token=refresh_token)
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh-токен невалиден или просрочен",
            )

        token_type = refresh_payload.get(TOKEN_TYPE_FIELD)
        if token_type != REFRESH_TOKEN_TYPE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Ожидался refresh-токен, получен: {token_type}",
            )

        entity_id = int(refresh_payload.get("sub"))
        entity = await self.repo.get_auth_entity_by_id(entity_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден",
            )

        access_token = await auth.create_access_token(auth_info=entity)
        await auth.set_token_cookie(
            response=response,
            key=ACCESS_TOKEN_COOKIE_KEY,
            value=access_token,
            max_age=settings.auth.access_expire_min * 60,
        )
        return entity

    # ── Payload из запроса ───────────────────────────────────────────────────

    async def access_token_payload(
        self, request: Request, response: Response
    ) -> AccessTokenPayload:
        """
        Извлекает payload из access-токена.

        Порядок:
        1. Middleware уже декодировал → берём из request.state.auth_payload.
        2. Middleware пометил needs_refresh → обновляем через refresh-токен.
        3. Ничего нет → 401.
        """
        payload = getattr(request.state, "auth_payload", None)
        if payload:
            return AccessTokenPayload(**payload)

        if getattr(request.state, "token_needs_refresh", False):
            refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_KEY)
            if not refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Требуется аутентификация",
                )
            entity = await self.refresh_authentication(
                response=response, refresh_token=refresh_token
            )
            payload_dict = auth.create_payload(auth_payload=entity)
            return AccessTokenPayload(**payload_dict)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация",
        )

    # ── Сброс пароля ─────────────────────────────────────────────────────────

    async def password_reset_request(
        self, data: PasswordResetRequest
    ) -> PasswordResetResponse:
        """
        Генерирует ссылку для сброса пароля и публикует событие в RabbitMQ.
        Всегда возвращает одинаковый ответ — не раскрывает, есть ли email в БД.
        """
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
            token = await auth.encode_jwt(
                payload={
                    "sub": str(entity.id),
                    "email": entity.email,
                    "type": "password_reset",
                },
                expire_timedelta=timedelta(minutes=30),
            )
            reset_link = f"{settings.frontend_url}/reset-password?token={token}"
            
            from core.broker import broker
            from domain.entity.schemas import PasswordResetNotification
            
            message = PasswordResetNotification(
                to_email=entity.email,
                reset_link=reset_link,
            )
            await broker.publish(message, queue="password_reset_queue")
            
            return generic_response
        except Exception:
            logger.exception("Ошибка генерации токена сброса пароля для email=%s", email)
            return PasswordResetResponse(detail="Внутренняя ошибка. Попробуйте позже.")

    async def password_reset_confirm(self, data: PasswordResetConfirm) -> "PasswordResetResponse":
        if data.new_password != data.repeat_password:
            raise HTTPException(status_code=400, detail="Пароли не совпадают")

        try:
            payload = await auth.decode_jwt(data.token)
        except Exception:
            raise HTTPException(status_code=400, detail="Некорректный или просроченный токен")

        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=400, detail="Некорректный тип токена")

        entity_id = int(payload.get("sub"))
        entity = await self.repo.get_auth_entity_by_id(entity_id)
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

        new_hash = await auth.hash_password(data.new_password)
        await self.repo.update_password(entity_id, new_hash)
        return PasswordResetResponse(detail="Пароль успешно изменён")

    async def get_entity_by_id(self, entity_id: int) -> AuthEntity | None:
        return await self.repo.get_auth_entity_by_id(entity_id)


# ── RoleRequestService ────────────────────────────────────────────────────────


class RoleRequestService:
    def __init__(self, repo: RoleRequestRepository, entity_repo: AuthRepository) -> None:
        self.repo = repo
        self.entity_repo = entity_repo

    async def create_request(self, entity_id: int, data: RoleRequestCreate) -> RoleRequest:
        """Создать заявку на роль (только если нет активной pending-заявки)."""
        total, pending = await self.repo.list_requests(status=RoleRequestStatus.PENDING)
        if any(r.entity_id == entity_id for r in pending):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Активная заявка уже существует",
            )
        return await self.repo.create(
            entity_id=entity_id, requested_role=data.requested_desired_role
        )

    async def get_request(self, request_id: int) -> RoleRequest:
        req = await self.repo.get_by_id(request_id)
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заявка не найдена",
            )
        return req

    async def list_requests(
        self,
        status_: Optional[RoleRequestStatus],
        offset: int,
        limit: int,
    ) -> tuple[int, list[RoleRequest]]:
        return await self.repo.list_requests(status=status_, offset=offset, limit=limit)

    async def approve_request(self, request_id: int) -> RoleRequest:
        req = await self.get_request(request_id)
        if req.status != RoleRequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Заявка уже обработана",
            )
        await self.repo.update_role(entity_id=req.entity_id, new_role=req.requested_role)
        return await self.repo.update_status(request_id, RoleRequestStatus.APPROVED)

    async def reject_request(self, request_id: int) -> RoleRequest:
        req = await self.get_request(request_id)
        if req.status != RoleRequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Заявка уже обработана",
            )
        return await self.repo.update_status(request_id, RoleRequestStatus.REJECTED)
