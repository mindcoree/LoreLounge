from fastapi import Depends
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from .session import SessionDep

from domain.services.profile import ProfileService
from domain.services.ignore_list import IgnoreListService


async def get_profile_service(
        session: SessionDep
) -> ProfileService:
    return ProfileService(session=session)


ProfileServiceDep = Annotated[ProfileService, Depends(get_profile_service)]


async def get_ignore_list_service(
        session: SessionDep
) -> IgnoreListService:
    return IgnoreListService(session=session)

IgnoreListServiceDep = Annotated[IgnoreListService, Depends(get_ignore_list_service)]
