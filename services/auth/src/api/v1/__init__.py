from fastapi import APIRouter
from .auth import router as auth_router
from .roles import router as roles_router

router_v1 = APIRouter(prefix="/v1", tags=["V1 ENDPOINTS"])


router_v1.include_router(roles_router, prefix="/role-requests", tags=["role-requests"])
router_v1.include_router(auth_router, prefix="/auth", tags=["auth"])