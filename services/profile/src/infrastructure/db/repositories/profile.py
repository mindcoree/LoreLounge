from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.profile import Profile
from base import BaseRepository


class ProfileRepository(BaseRepository[Profile]):
    def __init__(self, session: AsyncSession):
        # Initialize the base repository with the Profile model and the database session
        super().__init__(
            model=Profile,
            session=session,
        )

    async def get_by_user_id(self,user_id:UUID) -> Profile | None:
        """Get a profile by the associated user ID"""
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self,name: str) -> Profile | None:
        """Find a profile by unique nickname (for public pages)"""
        query = select(self.model).where(self.model.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    
    



    

