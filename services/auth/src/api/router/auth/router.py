from fastapi import APIRouter, Response, status, HTTPException, Form, Cookie
import logging
from typing import Annotated
from uuid import UUID

from .dependencies import AuthServiceDep, PayloadEntity
from core.config import settings
from core.types import ACCESS_TOKEN_COOKIE_KEY, REFRESH_TOKEN_COOKIE_KEY
from core import security as auth
from domain.entity.schemas import (
    AuthEntityOut,
    AuthEntityIn,
    AuthCredentials,
    TokenInfo,
)

router = APIRouter()
logger = logging.getLogger(__name__)

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

@router.post(
    "/refresh",
    summary="Обновление access-токена",
)
async def refresh_token(
    response: Response,
    service: AuthServiceDep,
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_TOKEN_COOKIE_KEY)] = None,
):
    """Обновляет access-токен по refresh-токену из куки."""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh-токен отсутствует")
        
    result = await service.refresh_authentication(refresh_token)
    
    await auth.set_token_cookie(
        response=response,
        key=ACCESS_TOKEN_COOKIE_KEY,
        value=result["access_token"],
        max_age=settings.auth.access_expire_min * 60,
    )
    return {"status": "ok"}

@router.get(
    "/me",
    response_model=AuthEntityOut,
    summary="Информация о текущем пользователе",
)
async def get_current_user(payload: PayloadEntity) -> AuthEntityOut:
    """Возвращает данные из payload JWT без обращения к БД."""
    return AuthEntityOut(
        id=UUID(payload.sub),
        email=payload.email,
        role=payload.role,
    )

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из системы",
)
async def logout(response: Response) -> None:
    """Удаляет access_token and refresh_token из cookie."""
    for key in (ACCESS_TOKEN_COOKIE_KEY, REFRESH_TOKEN_COOKIE_KEY):
        response.delete_cookie(key=key, path="/", httponly=True, samesite="lax")

@router.get("/.well-known/jwks.json", tags=["Infra"], include_in_schema=False)
async def get_jwks():
    """
    Возвращает JWKS (параметры ключа закэшированы в security.py).
    """
    try:
        jwk = auth.get_jwk_params()
        return {"keys": [jwk]}
    except Exception as e:
        logger.error("JWKS Error: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Error generating security keys"
        )
