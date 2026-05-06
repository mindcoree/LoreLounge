from uuid import UUID

from fastapi import APIRouter, status
from dependencies.auth import GuardDep
from dependencies.session import SessionDep

from schemas.ignore_list import IgnoreUserResponse

router = APIRouter(tags=["Ignore List endpoints"]) # api/profile/


# ══════════════════════════════════════════
# 1. Ignore List (Protected Endpoints)
# ══════════════════════════════════════════

@router.get(
    "/me/ignored",
    response_model=list[IgnoreUserResponse],
    summary="Get My Ignore List",
    description="Retrieve the list of users that the currently authenticated user has ignored.",
    responses={
        200: {"description": "Successful retrieval of ignore list"},
        401: {
            "description": "Unauthorized - Invalid or missing authentication credentials"
        },
    },
)
async def get_my_ignore_list(
    guard: GuardDep,
    session: SessionDep,
):
    """Get the list of users that the current user has ignored"""
    pass


@router.post(
    "/me/ignored/{target_user_id}",
    summary="Ignore a User",
    description="Add a user to the currently authenticated user's ignore list.",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User successfully added to ignore list"},
        400: {"description": "Bad Request - Invalid target user ID"},
        401: {
            "description": "Unauthorized - Invalid or missing authentication credentials"
        },
    },
)
async def ignore_user(
    target_user_id: UUID,
    guard: GuardDep,
    session: SessionDep,
):
    """Add a user to the current user's ignore list"""
    pass


@router.delete(
    "/me/ignored/{target_user_id}",
    summary="Unignore a User",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Remove a user from the currently authenticated user's ignore list.",
    responses={
        204: {"description": "User successfully removed from ignore list"},
        400: {"description": "Bad Request - Invalid target user ID"},
        401: {
            "description": "Unauthorized - Invalid or missing authentication credentials"
        },
    },
)
async def remove_ignored_user(
    target_user_id: UUID,
    guard: GuardDep,
    session: SessionDep,
):
    """Remove a user from the current user's ignore list"""
    pass
