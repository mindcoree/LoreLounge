from fastapi import APIRouter, status

from api.dependencies import GuardDep, ProfileServiceDep
from api.schemas.profile import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)

router = APIRouter(tags=["Profile endpoints"])  # /profile/


# ══════════════════════════════════════════
# 1. Personal Profile (Protected Endpoints)
# ══════════════════════════════════════════


@router.put(
    "/me",
    response_model=ProfileResponse,
    summary="Create/Replace My Profile",
    description="Create or fully replace a profile for the currently authenticated user.",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Profile successfully created or replaced"},
        400: {"description": "Bad Request - Invalid input data"},
        409: {"description": "Conflict - Profile name is already taken"},
        401: {
            "description": "Unauthorized - Invalid or missing authentication credentials"
        },

    },
)
async def create_my_profile(
    guard: GuardDep,
    profile_data: ProfileCreate,
    profile_service: ProfileServiceDep,
):
    """Create or fully replace your profile.

    Repeating the same PUT request produces the same resulting profile state.
    """
    return await profile_service.replace_profile(
        user_id=guard, profile_data=profile_data
    )


@router.get(
    "/me",
    response_model=ProfileResponse,
    summary="Get My Profile",
    description="Retrieve the profile of the currently authenticated user.",
    responses={
        200: {"description": "Successful retrieval of user profile"},
        401: {
            "description": "Unauthorized - Invalid or missing authentication credentials"
        },
    },
)
async def get_my_profile(
    guard: GuardDep,
    profile_service: ProfileServiceDep,
):
    """Get your own profile information. This endpoint requires authentication and should return the profile data associated with the currently authenticated user."""
    return await profile_service.get_my_profile(user_id=guard)


@router.patch(
    "/me",
    response_model=ProfileResponse,
    summary="Update My Profile",
    description="Update the profile of the currently authenticated user.",
    responses={
        200: {"description": "Successful update of user profile"},
        400: {"description": "Bad Request - Invalid input data"},
        401: {
            "description": "Unauthorized - Invalid or missing authentication credentials"
        },
    },
)
async def update_my_profile(
    update_data: ProfileUpdate,
    guard: GuardDep,
    profile_service: ProfileServiceDep,
):
    """Update about yourself (name, bio)"""

    return await profile_service.patch_profile(
        user_id=guard,
        update_data=update_data,
    )


# ══════════════════════════════════════════
# 3. Public Data (Open Endpoints)
# ══════════════════════════════════════════


@router.get(
    "/{name}",
    response_model=ProfileResponse,
    summary="Get Public Profile",
    description="Retrieve a public profile by name.",
)
async def get_public_profile(
    name: str,
    profile_service: ProfileServiceDep,
):
    # TODO: Implement logic to retrieve a public profile by name
    """This endpoint is open and does not require authentication. It should return public information about the user profile based on the provided name."""
    return await profile_service.get_by_name(name=name)
