from typing import cast, Any
from uuid import UUID
from sqlalchemy import and_, delete, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.models.ignore_list import IgnoreList
from infrastructure.db.repositories.base import BaseRepository

class IgnoreListRepository(BaseRepository[IgnoreList]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=IgnoreList, session=session)

    async def get_ignored_users(self, user_id: UUID, limit: int, offset: int) -> list[IgnoreList]:
        """
        Get all users ignored by the given user.
        selectinload fetches the ignored profile in the same query,
        preventing N+1 query problem.
        """
        query = (
            select(IgnoreList)
            .where(IgnoreList.user_id == user_id)
            .options(selectinload(IgnoreList.ignored))  # Eagerly load 'ignored' relation
            .order_by(IgnoreList.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_ignored_users(self, user_id: UUID) -> int:
        query = select(func.count()).select_from(IgnoreList).where(IgnoreList.user_id == user_id)
        result = await self.session.execute(query)
        return int(result.scalar_one())

    async def check_ignore_exists(self, user_id: UUID, ignored_user_id: UUID) -> bool:
        """Check if user is already in the ignore list"""
        query = select(IgnoreList).where(
            and_(
                IgnoreList.user_id == user_id,
                IgnoreList.ignored_user_id == ignored_user_id
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def remove_ignore(self, user_id: UUID, ignored_user_id: UUID) -> bool:
        """Remove user from ignore list by user ID and ignored user ID"""
        query = delete(IgnoreList).where(
            and_(
                IgnoreList.user_id == user_id,
                IgnoreList.ignored_user_id == ignored_user_id
            )
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return cast(Any, result).rowcount > 0