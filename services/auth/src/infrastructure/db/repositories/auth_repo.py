"""
Репозиторий для работы с AuthEntity через AsyncSession.
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError

from domain.entity.repository import AbstractAuthRepository
from infrastructure.db.models import AuthEntity, PasswordResetToken
from domain.entity.schemas import DomainAuthEntity, DomainPasswordResetToken
from domain.common.exceptions import UserAlreadyExistsError

logger = logging.getLogger(__name__)


def _to_domain_entity(entity: AuthEntity | None) -> DomainAuthEntity | None:
    if not entity:
        return None
    return DomainAuthEntity(
        id=entity.id,
        login=entity.login,
        email=entity.email,
        role=entity.role,
        hash_password=entity.hash_password
    )

def _to_domain_token(token: PasswordResetToken | None) -> DomainPasswordResetToken | None:
    if not token:
        return None
    return DomainPasswordResetToken(
        id=token.id,
        entity_id=token.entity_id,
        token_hash=token.token_hash,
        expires_at=token.expires_at,
        used=token.used
    )



class AuthSQLAlchemyRepository(AbstractAuthRepository):
    """CRUD-операции над таблицей auth_entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_entity(self, auth_data: dict) -> DomainAuthEntity:
        auth_entity = AuthEntity(**auth_data)
        self.session.add(auth_entity)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise UserAlreadyExistsError("Пользователь с таким email или логином уже существует")
            
        await self.session.refresh(auth_entity)
        return _to_domain_entity(auth_entity)

    async def get_auth_entity_by_id(self, id_entity: UUID) -> DomainAuthEntity | None:
        entity = await self.session.get(AuthEntity, id_entity)
        return _to_domain_entity(entity)

    async def get_auth_entity_by_email(self, email: str) -> DomainAuthEntity | None:
        stmt = select(AuthEntity).where(AuthEntity.email == email)
        result = await self.session.execute(stmt)
        return _to_domain_entity(result.scalar_one_or_none())

    async def get_auth_entity_for_verify(self, login: str) -> DomainAuthEntity | None:
        stmt = select(AuthEntity).where(AuthEntity.login == login)
        result = await self.session.execute(stmt)
        return _to_domain_entity(result.scalar_one_or_none())

    async def update_password(self, entity_id: UUID, new_hash_password: str) -> DomainAuthEntity | None:
        stmt = (
            update(AuthEntity)
            .where(AuthEntity.id == entity_id)
            .values(hash_password=new_hash_password)
            .returning(AuthEntity)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return _to_domain_entity(result.scalar_one_or_none())

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
    ) -> DomainPasswordResetToken:
        reset_token = PasswordResetToken(
            entity_id=entity_id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
        )
        self.session.add(reset_token)
        await self.session.commit()
        await self.session.refresh(reset_token)
        return _to_domain_token(reset_token)

    async def get_reset_token_by_hash(self, token_hash: str) -> DomainPasswordResetToken | None:
        stmt = select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return _to_domain_token(result.scalar_one_or_none())

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
