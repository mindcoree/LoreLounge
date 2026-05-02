from fastapi import APIRouter
from .auth.router import router as sub_auth_router
from .roles.router import router as roles_router
from .password.router import router as password_router

# Основной роутер, который объединяет все подразделы аутентификации
auth_router = APIRouter()

# Включаем роутеры БЕЗ дополнительных префиксов, так как префикс /auth будет в main.py
auth_router.include_router(sub_auth_router, tags=["Auth"])
auth_router.include_router(roles_router, tags=["Roles"])
auth_router.include_router(password_router, tags=["Password"])