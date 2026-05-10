from fastapi import Depends
from typing import Annotated

from .session import SessionDep

from domain.services.factory import create_profile_service
from domain.services.profile import ProfileService
from domain.services.ignore_list import IgnoreListService
from domain.services.media import MediaService


async def get_profile_service(
        session: SessionDep
) -> ProfileService:
    return create_profile_service(session=session)


ProfileServiceDep = Annotated[ProfileService, Depends(get_profile_service)]


async def get_ignore_list_service(
        session: SessionDep
) -> IgnoreListService:
    return IgnoreListService(session=session)

IgnoreListServiceDep = Annotated[IgnoreListService, Depends(get_ignore_list_service)]


async def get_media_service() -> MediaService:
    return MediaService()


MediaServiceDep = Annotated[MediaService, Depends(get_media_service)]
