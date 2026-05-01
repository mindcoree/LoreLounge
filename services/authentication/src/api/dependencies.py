"""
FastAPI dependencies для auth-service.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, Response, status

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
    response: Response,
    service: AuthServiceDep,
) -> AccessTokenPayload:
    return await service.access_token_payload(request, response)


PayloadEntity = Annotated[AccessTokenPayload, Depends(get_payload)]


# ── RBAC helper ───────────────────────────────────────────────────────────────


async def restrict_to_entity(
    payload: PayloadEntity,
    role_entity: Role,
) -> AccessTokenPayload:
    """Разрешить только нужную роль (или ADMIN)."""
    if payload.role == Role.ADMIN:
        return payload
    if payload.role != role_entity:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Доступ запрещён: требуется роль '{role_entity.value}'",
        )
    return payload


# ── RoleRequestService ────────────────────────────────────────────────────────


async def get_role_request_service(session: SessionDep) -> RoleRequestService:
    return RoleRequestService(
        repo=RoleRequestRepository(session=session),
        entity_repo=AuthRepository(session=session),
    )


RoleRequestServiceDep = Annotated[RoleRequestService, Depends(get_role_request_service)]
