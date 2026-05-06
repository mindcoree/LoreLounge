from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from domain.exceptions.ignore_list import (
    SelfIgnoreError,
    UserAlreadyIgnoredError,
    UserNotInIgnoreListError,
)
from infrastructure.db.models.ignore_list import IgnoreList
from infrastructure.db.repositories.ignore_list import IgnoreListRepository


class IgnoreListService:
    def __init__(self, session: AsyncSession):
        self.session = session
        # Service is responsible for its own repositories, ensuring they share the same session and transaction context
        self.ignore_list_repo = IgnoreListRepository(session)

    async def add_ignored_user(self, user_id: UUID, ignored_user_id: UUID) -> None:
        """
        Add a user to the ignore list.
        Raises SelfIgnoreError if user tries to ignore themselves.
        Raises UserAlreadyIgnoredError if user is already ignored.
        """
        # Prevent user from ignoring themselves
        if user_id == ignored_user_id:
            raise SelfIgnoreError()

        # Check if user is already ignored
        exists = await self.ignore_list_repo.check_ignore_exists(user_id, ignored_user_id)
        if exists:
            raise UserAlreadyIgnoredError(ignored_user_id)

        # Create the ignore entry
        await self.ignore_list_repo.create(
            user_id=user_id,
            ignored_user_id=ignored_user_id,
        )

        # Commit the transaction
        await self.session.commit()

    async def remove_ignored_user(self, user_id: UUID, ignored_user_id: UUID) -> None:
        """
        Remove a user from the ignore list.
        Raises UserNotInIgnoreListError if user is not in the ignore list.
        """
        removed = await self.ignore_list_repo.remove_ignore(user_id, ignored_user_id)
        if not removed:
            raise UserNotInIgnoreListError(ignored_user_id)

        # Commit the transaction
        await self.session.commit()

    async def get_ignore_list(self, user_id: UUID, limit: int, offset: int) -> tuple[list[IgnoreList], int]:
        """Get all users ignored by the given user"""
        ignored_users = await self.ignore_list_repo.get_ignored_users(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        total = await self.ignore_list_repo.count_ignored_users(user_id=user_id)
        return ignored_users, total

    async def is_user_ignored(self, user_id: UUID, ignored_user_id: UUID) -> bool:
        """Check if a user is in the ignore list"""
        return await self.ignore_list_repo.check_ignore_exists(user_id, ignored_user_id)
    