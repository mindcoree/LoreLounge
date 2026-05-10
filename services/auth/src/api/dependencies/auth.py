from typing import Annotated
from fastapi import Depends, HTTPException, Request, status

from domain.enums import Role
from api.schemas.auth import AccessTokenPayload
from .service import AuthServiceDep


async def get_payload(
    request: Request,
    service: AuthServiceDep,
) -> AccessTokenPayload:
    return await service.access_token_payload(dict(request.headers))


PayloadEntity = Annotated[AccessTokenPayload, Depends(get_payload)]


async def require_admin(payload: PayloadEntity) -> AccessTokenPayload:
    """Разрешить доступ только администратору."""
    if payload.role == Role.ADMIN:
        return payload
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Доступ запрещён: требуется роль 'admin'",
    )


AdminGuard = Annotated[AccessTokenPayload, Depends(require_admin)]
