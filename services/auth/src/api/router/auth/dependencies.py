from typing import Annotated
from fastapi import Depends, HTTPException, Request, status

from domain.common.enums import Role
from domain.entity.schemas import AccessTokenPayload
from domain.entity.services import AuthServices
from infrastructure.db.session import SessionDep
from infrastructure.db.repositories.auth_repo import AuthSQLAlchemyRepository
from domain.role_requests.repository import RoleRequestRepository
from infrastructure.broker.rabbitmq import broker

async def get_auth_service(session: SessionDep) -> AuthServices:
    return AuthServices(
        repository=AuthSQLAlchemyRepository(session=session),
        message_broker=broker,
        role_request_repo=RoleRequestRepository(session=session),
    )

AuthServiceDep = Annotated[AuthServices, Depends(get_auth_service)]

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
