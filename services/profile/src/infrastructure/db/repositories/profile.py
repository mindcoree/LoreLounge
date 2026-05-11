from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.mappers import map_profile_integrity_error
from infrastructure.db.models.profile import Profile
from infrastructure.db.repositories.base import BaseRepository


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

    async def create_profile(
        self,
        *,
        user_id: UUID,
        name: str,
        bio: str | None,
        avatar_url: str | None,
        background_url: str | None,
        birth_date,
        gender,
    ) -> Profile:
        try:
            return await self.create(
                user_id=user_id,
                name=name,
                bio=bio,
                avatar_url=avatar_url,
                background_url=background_url,
                birth_date=birth_date,
                gender=gender,
            )
        except IntegrityError as exc:
            raise map_profile_integrity_error(
                exc,
                user_id=user_id,
                name=name,
            ) from exc

    async def update_profile(self, profile_id: int, **kwargs) -> Profile | None:
        try:
            return await self.update(profile_id, **kwargs)
        except IntegrityError as exc:
            raise map_profile_integrity_error(exc, name=kwargs.get("name")) from exc

    async def delete_by_user_id(self, user_id: UUID) -> bool:
        profile = await self.get_by_user_id(user_id)
        if not profile:
            return False

        await self.session.delete(profile)
        await self.session.flush()
        return True
    
    
    



    

