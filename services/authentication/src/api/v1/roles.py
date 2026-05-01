"""
API v1: эндпоинты управления заявками на роль (только MODERATOR / ADMIN).
"""

from typing import Optional
from fastapi import APIRouter, status, Query

from api.dependencies import PayloadEntity, RoleRequestServiceDep
from domain.common.enums import RoleRequestStatus
from domain.entity.schemas import RoleRequestOut, RoleRequestListOut

router = APIRouter()


@router.get(
    "/",
    response_model=RoleRequestListOut,
    summary="Список заявок на смену роли",
)
async def list_role_requests(
    payload: PayloadEntity,
    service: RoleRequestServiceDep,
    status_filter: Optional[RoleRequestStatus] = Query(None, alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> RoleRequestListOut:
    """Возвращает список заявок (с пагинацией и фильтрацией по статусу)."""
    total, items = await service.list_requests(
        status_=status_filter, offset=offset, limit=limit
    )
    return RoleRequestListOut(total=total, items=list(items))


@router.post(
    "/{request_id}/approve",
    response_model=RoleRequestOut,
    summary="Одобрить заявку на роль",
)
async def approve_role_request(
    request_id: int,
    payload: PayloadEntity,
    service: RoleRequestServiceDep,
) -> RoleRequestOut:
    """Одобряет заявку: меняет роль пользователя и статус заявки → APPROVED."""
    return await service.approve_request(request_id)


@router.post(
    "/{request_id}/reject",
    response_model=RoleRequestOut,
    summary="Отклонить заявку на роль",
)
async def reject_role_request(
    request_id: int,
    payload: PayloadEntity,
    service: RoleRequestServiceDep,
) -> RoleRequestOut:
    """Отклоняет заявку: статус → REJECTED."""
    return await service.reject_request(request_id)
