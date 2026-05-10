from fastapi import APIRouter
from config.settings import settings

from .auth import router as sub_auth_router
from .roles import router as roles_router
from .password import router as password_router

# Основной роутер, который объединяет все подразделы аутентификации
router = APIRouter(prefix=settings.api.prefix)

router.include_router(sub_auth_router)
router.include_router(roles_router)
router.include_router(password_router)
