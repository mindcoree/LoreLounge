from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas.profile import ProfileCreate, ProfileUpdate
from domain.exceptions import ProfileAlreadyExistsError, ProfileNotFoundError
from infrastructure.db.repositories.profile import ProfileRepository
from infrastructure.storage.minio_client import delete_user_media_from_minio

class ProfileService:
    def __init__(self, session: AsyncSession):
        self.session = session
        # initializing repositories inside the service ensures they share the same session and transaction context, which is crucial for maintaining data integrity across multiple operations within the same business logic execution.
        self.profile_repo = ProfileRepository(session)

    async def create_profile(self, user_id: UUID, profile_data: ProfileCreate):
        """Create a new profile for a user."""
        # 1. Check if profile already exists
        existing_profile = await self.profile_repo.get_by_user_id(user_id)
        if existing_profile:
            raise ProfileAlreadyExistsError(user_id)
        
        # 2. Check if the name is already taken
        existing_name = await self.profile_repo.get_by_name(profile_data.name)
        if existing_name:
            raise ProfileAlreadyExistsError(user_id)
        
        # 3. Create the profile
        profile = await self.profile_repo.create(
            user_id=user_id,
            name=profile_data.name,
            bio=profile_data.bio,
            avatar_url=profile_data.avatar_url,
            background_url=profile_data.background_url,
            birth_date=profile_data.birth_date,
            gender=profile_data.gender,
        )
        
        # 4. Commit the transaction
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def get_my_profile(self, user_id: UUID):
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFoundError(user_id)
        return profile

    async def get_by_name(self,name: str):
        profile = await self.profile_repo.get_by_name(name)
        if not profile:
            raise ProfileNotFoundError(name)
        return profile


    async def delete_my_profile(self, user_id: UUID) -> bool:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            return False

        await self.session.delete(profile)
        await self.session.commit()
        return True

    async def delete_account_data(self, user_id: UUID) -> bool:
        await delete_user_media_from_minio(user_id)
        return await self.delete_my_profile(user_id)
    

    async def update_my_profile(self, user_id: UUID, update_data: ProfileUpdate):
        # 1. Check if the profile exists, if not - raise an error (we don't want to create a new one here)
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFoundError(user_id)

        # 2. Prepare the update data (exclude None values, keep only what the user actually sent)
        update_dict = update_data.model_dump(exclude_unset=True)
        
        if not update_dict:
            return profile # If no updates were provided, return the current profile

        # 3. Additional logic: if name is being updated, check if it's already taken
        if "name" in update_dict and update_dict["name"]:
            existing_name = await self.profile_repo.get_by_name(update_dict["name"])
            if existing_name and existing_name.user_id != user_id:
                raise ProfileAlreadyExistsError(user_id)

        # 4. Perform the update in the database (the repository will make the flush)
        updated_profile = await self.profile_repo.update(profile.id, **update_dict)

        # 5. Commit the transaction!
        await self.session.commit()
        await self.session.refresh(updated_profile) 
        return updated_profile
    