from typing import Annotated, Optional
from fastapi import APIRouter, Query, Form
from uuid import UUID

from api.dependencies.auth import AdminGuard, PayloadEntity
from api.dependencies.service import RoleRequestServiceDep
from domain.enums import RoleRequestStatus
from api.schemas.roles import RoleRequestCreate, RoleRequestOut, RoleRequestListOut

router = APIRouter(tags=["Roles"])

@router.post(
    "/role-request",
    response_model=RoleRequestOut,
    summary="Создать заявку на смену роли",
)
async def create_role_request(
    data: Annotated[RoleRequestCreate, Form()],
    service: RoleRequestServiceDep,
    payload: PayloadEntity,
) -> RoleRequestOut:
    """Создаёт заявку на смену роли для текущего пользователя."""
    return await service.create_request(entity_id=UUID(payload.sub), data=data)

@router.get(
    "/role-requests/",
    response_model=RoleRequestListOut,
    summary="Список заявок на смену роли",
)
async def list_role_requests(
    _admin: AdminGuard,
    service: RoleRequestServiceDep,
    status_filter: Optional[RoleRequestStatus] = Query(None, alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> RoleRequestListOut:
    """Возвращает список заявок (только для администратора)."""
    total, items = await service.list_requests(
        status_=status_filter, offset=offset, limit=limit
    )
    return RoleRequestListOut(
        total=total,
        items=[RoleRequestOut.model_validate(item) for item in items],
    )

@router.post(
    "/role-requests/{request_id}/approve",
    response_model=RoleRequestOut,
    summary="Одобрить заявку на роль",
)
async def approve_role_request(
    request_id: int,
    _admin: AdminGuard,
    service: RoleRequestServiceDep,
) -> RoleRequestOut:
    """Одобряет заявку: меняет роль пользователя и статус заявки → APPROVED."""
    request = await service.approve_request(request_id)
    return RoleRequestOut.model_validate(request)

@router.post(
    "/role-requests/{request_id}/reject",
    response_model=RoleRequestOut,
    summary="Отклонить заявку на роль",
)
async def reject_role_request(
    request_id: int,
    _admin: AdminGuard,
    service: RoleRequestServiceDep,
) -> RoleRequestOut:
    """Отклоняет заявку: статус → REJECTED."""
    request = await service.reject_request(request_id)
    return RoleRequestOut.model_validate(request)
