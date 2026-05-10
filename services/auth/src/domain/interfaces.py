"""
Abstract interfaces for auth domain.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional
from uuid import UUID


class AbstractMessageBroker(ABC):
    @abstractmethod
    async def publish(self, message: Any, queue: str) -> None:
        pass


class AbstractAuthRepository(ABC):
    @abstractmethod
    async def create_entity(self, auth_data: dict) -> Any:
        pass

    @abstractmethod
    async def get_auth_entity_by_id(self, id_entity: UUID) -> Any:
        pass

    @abstractmethod
    async def get_auth_entity_by_email(self, email: str) -> Any:
        pass

    @abstractmethod
    async def update_password(self, entity_id: UUID, new_hash_password: str) -> Any:
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
    ) -> Any:
        pass

    @abstractmethod
    async def get_reset_token_by_hash(self, token_hash: str) -> Any:
        pass

    @abstractmethod
    async def mark_reset_token_used(self, token_id: int) -> None:
        pass

    @abstractmethod
    async def cleanup_reset_tokens(self, now: datetime) -> None:
        pass

    @abstractmethod
    async def delete_reset_tokens_by_entity_id(self, entity_id: UUID) -> None:
        pass

    @abstractmethod
    async def delete_auth_entity(self, entity_id: UUID) -> None:
        pass
