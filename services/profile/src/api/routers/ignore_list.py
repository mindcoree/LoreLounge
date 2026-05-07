from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, status, Query

from api.dependencies import GuardDep, IgnoreListServiceDep
from api.schemas.ignore_list import IgnoreListPageResponse, IgnoreUserResponse
from api.schemas.profile import ProfileResponse
from api.schemas.pagination import Pagination

router = APIRouter(tags=["Ignore List endpoints"]) # /profile/


# ══════════════════════════════════════════
# 1. Ignore List (Protected Endpoints)
# ══════════════════════════════════════════

@router.get(
    "/me/ignored",
    response_model=IgnoreListPageResponse,
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
    ignore_list_service: IgnoreListServiceDep,
    pagination: Annotated[Pagination, Query()],
):
    """Get the list of users that the current user has ignored"""
    ignored_users, total = await ignore_list_service.get_ignore_list(
        user_id=guard,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    items = [
        IgnoreUserResponse(
            ignored_user_id=ignore_entry.ignored_user_id,
            ignored_profile=(
                ProfileResponse.model_validate(ignore_entry.ignored, from_attributes=True)
                if ignore_entry.ignored is not None
                else None
            ),
        )
        for ignore_entry in ignored_users
    ]
    return IgnoreListPageResponse(
        items=items,
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


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
    ignore_list_service: IgnoreListServiceDep,
):
    """Add a user to the current user's ignore list"""
    await ignore_list_service.add_ignored_user(
        user_id=guard,
        ignored_user_id=target_user_id,
    )
    return {"detail": "User successfully added to ignore list"}


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
    ignore_list_service: IgnoreListServiceDep,
):
    """Remove a user from the current user's ignore list"""
    await ignore_list_service.remove_ignored_user(
        user_id=guard,
        ignored_user_id=target_user_id,
    )
