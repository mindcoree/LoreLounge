from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from datetime import datetime

from domain.entity.schemas import DomainAuthEntity, DomainPasswordResetToken


class AbstractAuthRepository(ABC):
    @abstractmethod
    async def create_entity(self, auth_data: dict) -> DomainAuthEntity:
        pass

    @abstractmethod
    async def get_auth_entity_by_id(self, id_entity: UUID) -> Optional[DomainAuthEntity]:
        pass

    @abstractmethod
    async def get_auth_entity_by_email(self, email: str) -> Optional[DomainAuthEntity]:
        pass

    @abstractmethod
    async def get_auth_entity_for_verify(self, login: str) -> Optional[DomainAuthEntity]:
        pass

    @abstractmethod
    async def update_password(self, entity_id: UUID, new_hash_password: str) -> Optional[DomainAuthEntity]:
        pass

    @abstractmethod
    async def invalidate_reset_tokens(self, entity_id: UUID) -> None:
        pass

    @abstractmethod
    async def create_reset_token(
        self,
        entity_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> DomainPasswordResetToken:
        pass

    @abstractmethod
    async def get_reset_token_by_hash(self, token_hash: str) -> Optional[DomainPasswordResetToken]:
        pass

    @abstractmethod
    async def mark_reset_token_used(self, token_id: int) -> None:
        pass

    @abstractmethod
    async def cleanup_reset_tokens(self, now: datetime) -> None:
        pass
