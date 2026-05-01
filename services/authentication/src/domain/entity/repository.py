"""
Репозиторий для работы с AuthEntity и RoleRequest через AsyncSession.

Все методы полностью асинхронные (asyncpg + SQLAlchemy 2.0).
"""

import logging
from datetime import datetime
from typing import Sequence, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, update, func

from domain.common.enums import DesiredRole, RoleRequestStatus
from infrastructure.db.models import AuthEntity, RoleRequest, PasswordResetToken

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

    async def get_auth_entity_by_id(self, id_entity: UUID) -> AuthEntity | None:
        return await self.session.get(AuthEntity, id_entity)

    async def get_auth_entity_by_email(self, email: str) -> AuthEntity | None:
        stmt = select(AuthEntity).where(AuthEntity.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_auth_entity_for_verify(self, login: str) -> AuthEntity | None:
        stmt = select(AuthEntity).where(AuthEntity.login == login)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_password(self, entity_id: UUID, new_hash_password: str) -> AuthEntity | None:
        stmt = (
            update(AuthEntity)
            .where(AuthEntity.id == entity_id)
            .values(hash_password=new_hash_password)
            .returning(AuthEntity)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def invalidate_reset_tokens(self, entity_id: UUID) -> None:
        stmt = (
            update(PasswordResetToken)
            .where(PasswordResetToken.entity_id == entity_id)
            .where(PasswordResetToken.used.is_(False))
            .values(used=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def create_reset_token(
        self,
        entity_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> PasswordResetToken:
        reset_token = PasswordResetToken(
            entity_id=entity_id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
        )
        self.session.add(reset_token)
        await self.session.commit()
        await self.session.refresh(reset_token)
        return reset_token

    async def get_reset_token_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        stmt = select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_reset_token_used(self, token_id: int) -> None:
        stmt = (
            update(PasswordResetToken)
            .where(PasswordResetToken.id == token_id)
            .values(used=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def cleanup_reset_tokens(self, now: datetime) -> None:
        stmt = delete(PasswordResetToken).where(
            (PasswordResetToken.expires_at <= now) | (PasswordResetToken.used.is_(True))
        )
        await self.session.execute(stmt)
        await self.session.commit()



