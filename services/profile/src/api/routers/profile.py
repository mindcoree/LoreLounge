from fastapi import APIRouter
from dependencies.auth import GuardDep
from dependencies.session import SessionDep

from schemas.profile import ProfileUpdate, ProfileResponse
from schemas.ignore_list import IgnoreUserResponse

router = APIRouter(tags=["Profile endpoints"]) # api/profile/


# ══════════════════════════════════════════
# 1. Personal Profile (Protected Endpoints)
# ══════════════════════════════════════════


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
    session: SessionDep,
):
    # TODO: Implement logic to retrieve the current user's profile using guard (user_id)
    pass


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
    session: SessionDep,
):
    """Update about yourself (name, bio)"""

    # TODO: Implement logic to update the current user's profile using guard (user_id)
    pass


# ══════════════════════════════════════════
# 3. Public Data (Open Endpoints)
# ══════════════════════════════════════════


@router.get(
    "/{name}",
    response_model=ProfileResponse,
    summary="Get Public Profile",
    description="Retrieve a public profile by name.",
)
async def get_public_profile(name: str):
    # TODO: Implement logic to retrieve a public profile by name
    """This endpoint is open and does not require authentication. It should return public information about the user profile based on the provided name."""
    pass
