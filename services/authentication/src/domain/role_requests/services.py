import logging
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from domain.common.enums import RoleRequestStatus
from domain.entity.repository import AuthRepository
from domain.role_requests.repository import RoleRequestRepository
from domain.role_requests.schemas import RoleRequestCreate
from infrastructure.db.models import RoleRequest

logger = logging.getLogger(__name__)

class RoleRequestService:
    def __init__(self, repo: RoleRequestRepository, entity_repo: AuthRepository) -> None:
        self.repo = repo
        self.entity_repo = entity_repo

    async def create_request(self, entity_id: UUID, data: RoleRequestCreate) -> RoleRequest:
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
