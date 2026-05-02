import logging
from typing import Optional
from uuid import UUID

from domain.common.enums import RoleRequestStatus
from domain.entity.repository import AbstractAuthRepository
from domain.role_requests.repository import RoleRequestRepository
from domain.role_requests.schemas import RoleRequestCreate
from infrastructure.db.models import RoleRequest
from domain.common.exceptions import (
    RoleRequestAlreadyExistsError,
    RoleRequestNotFoundError,
    RoleRequestAlreadyProcessedError,
)

logger = logging.getLogger(__name__)

class RoleRequestService:
    def __init__(self, repo: RoleRequestRepository, entity_repo: AbstractAuthRepository) -> None:
        self.repo = repo
        self.entity_repo = entity_repo

    async def create_request(self, entity_id: UUID, data: RoleRequestCreate) -> RoleRequest:
        """Создать заявку на роль (только если нет активной pending-заявки)."""
        total, pending = await self.repo.list_requests(status=RoleRequestStatus.PENDING)
        if any(r.entity_id == entity_id for r in pending):
            raise RoleRequestAlreadyExistsError("Активная заявка уже существует")
        
        return await self.repo.create(
            entity_id=entity_id, requested_role=data.requested_desired_role
        )

    async def get_request(self, request_id: int) -> RoleRequest:
        req = await self.repo.get_by_id(request_id)
        if not req:
            raise RoleRequestNotFoundError("Заявка не найдена")
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
            raise RoleRequestAlreadyProcessedError("Заявка уже обработана")
            
        await self.repo.update_role(entity_id=req.entity_id, new_role=req.requested_role)
        return await self.repo.update_status(request_id, RoleRequestStatus.APPROVED)

    async def reject_request(self, request_id: int) -> RoleRequest:
        req = await self.get_request(request_id)
        if req.status != RoleRequestStatus.PENDING:
            raise RoleRequestAlreadyProcessedError("Заявка уже обработана")
            
        return await self.repo.update_status(request_id, RoleRequestStatus.REJECTED)
