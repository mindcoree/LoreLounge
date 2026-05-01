"""
Репозиторий для работы с AuthEntity и RoleRequest через AsyncSession.

Все методы полностью асинхронные (asyncpg + SQLAlchemy 2.0).
"""

import logging
from typing import Sequence, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from domain.common.enums import DesiredRole, RoleRequestStatus
from infrastructure.db.models import AuthEntity, RoleRequest

logger = logging.getLogger(__name__)


class AuthRepository:
    """CRUD-операции над таблицей auth_entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_entity(self, auth_data: dict) -> AuthEntity:
        """Создать нового пользователя и закоммитить транзакцию."""
        auth_entity = AuthEntity(**auth_data)
        self.session.add(auth_entity)
        await self.session.commit()
        await self.session.refresh(auth_entity)
        return auth_entity

    async def get_auth_entity_by_id(self, id_entity: int) -> AuthEntity | None:
        return await self.session.get(AuthEntity, id_entity)

    async def get_auth_entity_by_email(self, email: str) -> AuthEntity | None:
        stmt = select(AuthEntity).where(AuthEntity.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_auth_entity_for_verify(self, login: str) -> AuthEntity | None:
        stmt = select(AuthEntity).where(AuthEntity.login == login)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_password(self, entity_id: int, new_hash_password: str) -> AuthEntity | None:
        stmt = (
            update(AuthEntity)
            .where(AuthEntity.id == entity_id)
            .values(hash_password=new_hash_password)
            .returning(AuthEntity)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()


class RoleRequestRepository:
    """CRUD-операции над таблицей role_requests."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entity_id: int, requested_role: DesiredRole) -> RoleRequest:
        role_request = RoleRequest(entity_id=entity_id, requested_role=requested_role)
        self.session.add(role_request)
        await self.session.commit()
        await self.session.refresh(role_request)
        return role_request

    async def get_by_id(self, request_id: int) -> Optional[RoleRequest]:
        stmt = select(RoleRequest).where(RoleRequest.id == request_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_requests(
        self,
        status: Optional[RoleRequestStatus] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[int, Sequence[RoleRequest]]:
        stmt = select(RoleRequest)
        if status is not None:
            stmt = stmt.where(RoleRequest.status == status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self.session.scalar(count_stmt)

        stmt = stmt.offset(offset).limit(limit).order_by(RoleRequest.created_at.desc())
        result = await self.session.execute(stmt)
        return total or 0, result.scalars().all()

    async def update_role(self, entity_id: int, new_role: DesiredRole) -> AuthEntity | None:
        stmt = (
            update(AuthEntity)
            .where(AuthEntity.id == entity_id)
            .values(role=new_role)
            .returning(AuthEntity)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def update_status(
        self, request_id: int, status: RoleRequestStatus
    ) -> Optional[RoleRequest]:
        stmt = (
            update(RoleRequest)
            .where(RoleRequest.id == request_id)
            .values(status=status)
            .returning(RoleRequest)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()
