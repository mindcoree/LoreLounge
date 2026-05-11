from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas.profile import ProfileCreate, ProfileUpdate
from domain.exceptions import (
    ProfileConflictError,
    ProfileNameTakenError,
    ProfileNotFoundError,
    ProfileAlreadyExistsError,
    ProfileRepositoryInvariantError,
)
from infrastructure.db.models.profile import Profile
from infrastructure.db.repositories.profile import ProfileRepository
from infrastructure.storage import (
    MinioCleanupError,
    delete_user_media_from_minio,
)


class ProfileService:
    def __init__(self, session: AsyncSession):
        self.session = session
        # Keep repository bound to the same session so multi-step business flows stay atomic.
        self.profile_repo = ProfileRepository(session)

    async def _commit_and_refresh(self, profile: Profile) -> Profile:
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def _rollback(self) -> None:
        await self.session.rollback()

    async def replace_profile(
        self, user_id: UUID, profile_data: ProfileCreate
    ) -> Profile:
        """Create or fully replace a profile for a user (idempotent PUT semantics)."""
        # Preserve PUT idempotency: existing resource should be replaced, not rejected.
        existing_profile = await self.profile_repo.get_by_user_id(user_id)
        if existing_profile:
            return await self._replace_existing_profile(existing_profile, profile_data)

        # Fast fail on obvious name collision before opening write path.
        existing_name = await self.profile_repo.get_by_name(profile_data.name)
        if existing_name:
            raise ProfileNameTakenError(profile_data.name)

        try:
            profile = await self.profile_repo.create_profile(
                user_id=user_id,
                name=profile_data.name,
                bio=profile_data.bio,
                avatar_url=profile_data.avatar_url,
                background_url=profile_data.background_url,
                birth_date=profile_data.birth_date,
                gender=profile_data.gender,
            )

            # Expose the committed state to caller (timestamps/defaults may be DB-generated).
            return await self._commit_and_refresh(profile)
        except ProfileAlreadyExistsError:
            await self._rollback()
            # Concurrent create can win the race; re-read and apply replace to keep PUT deterministic.
            existing_profile = await self.profile_repo.get_by_user_id(user_id)
            if existing_profile:
                return await self._replace_existing_profile(
                    existing_profile, profile_data
                )
            raise
        except (ProfileNameTakenError, ProfileConflictError):
            await self._rollback()
            raise

    async def _replace_existing_profile(
        self,
        profile: Profile,
        profile_data: ProfileCreate,
    ) -> Profile:
        replacement_data = profile_data.model_dump()
        try:
            updated_profile = await self.profile_repo.update_profile(
                profile.id, **replacement_data
            )
            if not updated_profile:
                raise ProfileRepositoryInvariantError()
            return await self._commit_and_refresh(updated_profile)
        except (ProfileNameTakenError, ProfileConflictError):
            await self._rollback()
            raise

    async def get_my_profile(self, user_id: UUID) -> Profile:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFoundError(user_id)
        return profile

    async def get_by_name(self, name: str) -> Profile:
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
        # Persist DB deletion first: if commit fails, external files are still intact.
        if not await self.delete_my_profile(user_id):
            raise ProfileNotFoundError(user_id)

        # MinIO cleanup is best-effort because DB transaction is already committed.
        try:
            await delete_user_media_from_minio(user_id)
        except MinioCleanupError:
            logger.exception(
                "Failed to delete user media from MinIO",
                extra={"user_id": str(user_id)},
            )

        return True

    async def patch_profile(self, user_id: UUID, update_data: ProfileUpdate) -> Profile:
        # PATCH should never create resources; missing profile is a contract violation for this endpoint.
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFoundError(user_id)

        # Keep PATCH semantics: update only fields explicitly provided by the client.
        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            # Avoid unnecessary writes when request does not change state.
            return profile

        # Validate name uniqueness early to return stable domain-level errors.
        if "name" in update_dict and update_dict["name"]:
            existing_name = await self.profile_repo.get_by_name(update_dict["name"])
            if existing_name and existing_name.user_id != user_id:
                raise ProfileNameTakenError(update_dict["name"])

        # 4. Perform the update in the database (the repository will make the flush)
        try:
            updated_profile = await self.profile_repo.update_profile(
                profile.id, **update_dict
            )
            if not updated_profile:
                raise ProfileRepositoryInvariantError()

            # Return committed view so caller gets canonical DB state.
            return await self._commit_and_refresh(updated_profile)
        except (ProfileNameTakenError, ProfileConflictError):
            await self._rollback()
            raise
