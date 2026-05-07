from config.settings import settings

from fastapi import APIRouter

from .profile import router as profile_router
from .ignore_list import router as ignore_list_router
from .media import router as media_router

router = APIRouter(prefix=settings.api.prefix, tags=["API ENDPOINTS"])


router.include_router(profile_router)
router.include_router(ignore_list_router)
router.include_router(media_router)
