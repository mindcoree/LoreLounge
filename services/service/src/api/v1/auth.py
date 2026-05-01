"""
API v1: эндпоинты аутентификации LoreLounge.
"""

from fastapi import APIRouter, BackgroundTasks, Form, Response, status
from typing import Annotated

from api.dependencies import AuthServiceDep, PayloadEntity, RoleRequestServiceDep
from core.config import settings
from core.types import ACCESS_TOKEN_COOKIE_KEY, REFRESH_TOKEN_COOKIE_KEY
from core import security as auth
from domain.entity.schemas import (
    AuthEntityOut,
    AuthEntityIn,
    AuthCredentials,
    TokenInfo,
    RoleRequestCreate,
    RoleRequestOut,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
)

router = APIRouter()


# ── Регистрация ───────────────────────────────────────────────────────────────


@router.post(
    "/register",
    response_model=AuthEntityOut,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
async def register_entity(
    entity_in: Annotated[AuthEntityIn, Form()],
    service: AuthServiceDep,
) -> AuthEntityOut:
    """Регистрирует нового пользователя платформы LoreLounge."""
    return await service.register_entity(auth_in=entity_in)


# ── Вход ─────────────────────────────────────────────────────────────────────


@router.post(
    "/login",
    response_model=TokenInfo,
    summary="Вход в систему",
)
async def login(
    credentials: Annotated[AuthCredentials, Form()],
    service: AuthServiceDep,
    response: Response,
) -> TokenInfo:
    """
    Аутентифицирует пользователя, создаёт access + refresh токены
    и устанавливает их в http-only cookie.
    """
    auth_entity = await service.authenticate_entity(credentials)
    access_token = await auth.create_access_token(auth_info=auth_entity)
    refresh_token = await auth.create_refresh_token(auth_info=auth_entity)

    await auth.set_token_cookie(
        response=response,
        key=ACCESS_TOKEN_COOKIE_KEY,
        value=access_token,
        max_age=settings.auth.access_expire_min * 60,
    )
    await auth.set_token_cookie(
        response=response,
        key=REFRESH_TOKEN_COOKIE_KEY,
        value=refresh_token,
        max_age=settings.auth.refresh_expire_days * 24 * 60 * 60,
    )
    return TokenInfo(access=access_token, refresh=refresh_token)


# ── Текущий пользователь ──────────────────────────────────────────────────────


@router.get(
    "/me",
    response_model=AuthEntityOut,
    summary="Информация о текущем пользователе",
)
async def get_current_user(payload: PayloadEntity) -> AuthEntityOut:
    """Возвращает данные из payload JWT без обращения к БД."""
    return AuthEntityOut(
        id=int(payload.sub),
        email=payload.email,
        login=payload.login,
        role=payload.role,
    )


# ── Выход ─────────────────────────────────────────────────────────────────────


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из системы",
)
async def logout(response: Response) -> None:
    """Удаляет access_token и refresh_token из cookie."""
    for key in (ACCESS_TOKEN_COOKIE_KEY, REFRESH_TOKEN_COOKIE_KEY):
        response.delete_cookie(key=key, path="/", httponly=True, samesite="lax")


# ── Заявки на роль ────────────────────────────────────────────────────────────


@router.post(
    "/role-request",
    response_model=RoleRequestOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заявку на смену роли",
)
async def create_role_request(
    data: Annotated[RoleRequestCreate, Form()],
    service: RoleRequestServiceDep,
    payload: PayloadEntity,
) -> RoleRequestOut:
    """Создаёт заявку на смену роли для текущего пользователя."""
    return await service.create_request(entity_id=int(payload.sub), data=data)


# ── Сброс пароля ──────────────────────────────────────────────────────────────


@router.post(
    "/password-reset-request",
    response_model=PasswordResetResponse,
    summary="Запрос на сброс пароля",
)
async def password_reset_request(
    data: PasswordResetRequest,
    service: AuthServiceDep,
    background_tasks: BackgroundTasks,
) -> PasswordResetResponse:
    """Генерирует ссылку для сброса пароля и отправляет её на email в фоне."""
    response, email_data = await service.password_reset_request(data)
    if email_data:
        from utils.email import send_email  # Lazy import — сервис опционален
        background_tasks.add_task(
            send_email,
            email_data["to_email"],
            email_data["subject"],
            email_data["body"],
        )
    return response


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
