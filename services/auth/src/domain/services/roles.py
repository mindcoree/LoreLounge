"""
Сервис управления заявками на смену роли.
"""

import logging
from typing import Optional
from uuid import UUID

from domain.enums import RoleRequestStatus
from domain.interfaces import AbstractAuthRepository
from domain.exceptions import (
    RoleRequestAlreadyExistsError,
    RoleRequestNotFoundError,
    RoleRequestAlreadyProcessedError,
)
from api.schemas.roles import RoleRequestCreate

logger = logging.getLogger(__name__)


class RoleRequestService:
    def __init__(self, repo, entity_repo: AbstractAuthRepository) -> None:
        self.repo = repo
        self.entity_repo = entity_repo

    async def create_request(self, entity_id: UUID, data: RoleRequestCreate):
        """Создать заявку на роль (только если нет активной pending-заявки)."""
        total, pending = await self.repo.list_requests(status=RoleRequestStatus.PENDING)
        if any(r.entity_id == entity_id for r in pending):
            raise RoleRequestAlreadyExistsError()
        
        return await self.repo.create(
            entity_id=entity_id, requested_role=data.requested_desired_role
        )

    async def get_request(self, request_id: int):
        req = await self.repo.get_by_id(request_id)
        if not req:
            raise RoleRequestNotFoundError(request_id=request_id)
        return req

    async def list_requests(
        self,
        status_: Optional[RoleRequestStatus],
        offset: int,
        limit: int,
    ):
        return await self.repo.list_requests(status=status_, offset=offset, limit=limit)

    async def approve_request(self, request_id: int):
        req = await self.get_request(request_id)
        if req.status != RoleRequestStatus.PENDING:
            raise RoleRequestAlreadyProcessedError(request_id=request_id)
            
        await self.repo.update_role(entity_id=req.entity_id, new_role=req.requested_role)
        return await self.repo.update_status(request_id, RoleRequestStatus.APPROVED)

    async def reject_request(self, request_id: int):
        req = await self.get_request(request_id)
        if req.status != RoleRequestStatus.PENDING:
            raise RoleRequestAlreadyProcessedError(request_id=request_id)
            
        return await self.repo.update_status(request_id, RoleRequestStatus.REJECTED)
