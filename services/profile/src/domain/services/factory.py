from sqlalchemy.ext.asyncio import AsyncSession

from domain.services.profile import ProfileService


def create_profile_service(session: AsyncSession) -> ProfileService:
    return ProfileService(session=session)