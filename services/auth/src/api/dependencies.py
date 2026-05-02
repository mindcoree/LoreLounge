"""
FastAPI dependencies для auth.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from domain.common.enums import Role
from domain.entity.repository import AuthRepository
from domain.role_requests.repository import RoleRequestRepository
from domain.entity.schemas import AccessTokenPayload
from domain.entity.services import AuthServices
from domain.role_requests.services import RoleRequestService
from infrastructure.db.session import SessionDep


# ── AuthService ───────────────────────────────────────────────────────────────


async def get_auth_service(session: SessionDep) -> AuthServices:
    return AuthServices(
        repository=AuthRepository(session=session),
        role_request_repo=RoleRequestRepository(session=session),
    )


AuthServiceDep = Annotated[AuthServices, Depends(get_auth_service)]


# ── JWT Payload ───────────────────────────────────────────────────────────────


async def get_payload(
    request: Request,
    service: AuthServiceDep,
) -> AccessTokenPayload:
    return await service.access_token_payload(request)


PayloadEntity = Annotated[AccessTokenPayload, Depends(get_payload)]


# ── RBAC helper ───────────────────────────────────────────────────────────────


async def require_admin(payload: PayloadEntity) -> AccessTokenPayload:
    """Разрешить доступ только администратору."""
    if payload.role == Role.ADMIN:
        return payload
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Доступ запрещён: требуется роль 'admin'",
    )

AdminGuard = Annotated[AccessTokenPayload, Depends(require_admin)]

# ── RoleRequestService ────────────────────────────────────────────────────────


async def get_role_request_service(session: SessionDep) -> RoleRequestService:
    return RoleRequestService(
        repo=RoleRequestRepository(session=session),
        entity_repo=AuthRepository(session=session),
    )


RoleRequestServiceDep = Annotated[RoleRequestService, Depends(get_role_request_service)]
