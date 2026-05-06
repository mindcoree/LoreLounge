from fastapi import APIRouter, status, File, UploadFile
from typing import Optional

from api.dependencies import GuardDep, ProfileServiceDep, MediaServiceDep
from api.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate, UploadURLs

router = APIRouter(tags=["Profile endpoints"])  # api/profile/


# ══════════════════════════════════════════
# 1. Personal Profile (Protected Endpoints)
# ══════════════════════════════════════════


@router.post(
    "/me",
    response_model=ProfileResponse,
    summary="Create My Profile",
    description="Create a new profile for the currently authenticated user.",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Profile successfully created"},
        400: {"description": "Bad Request - Invalid input data"},
        401: {
            "description": "Unauthorized - Invalid or missing authentication credentials"
        },
        409: {"description": "Conflict - Profile already exists"},
    },
)
async def create_my_profile(
    guard: GuardDep,
    profile_data: ProfileCreate,
    profile_service: ProfileServiceDep,
):
    """Create a profile for yourself. This endpoint should only be called once per user, as each user can have only one profile. If a profile already exists for the user, it should return a 409 Conflict error."""
    return await profile_service.create_profile(user_id=guard, profile_data=profile_data)


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

    return await profile_service.update_my_profile(
        user_id=guard,
        update_data=update_data,
    )



# ══════════════════════════════════════════════════════════════════
# Upload endpoint: accept multipart files and return MinIO URLs only.
# ══════════════════════════════════════════════════════════════════

@router.post(
    "/me/upload",
    response_model=UploadURLs,
    summary="Upload media for profile",
    description="Uploads avatar/background to MinIO and returns their URLs.",
    status_code=status.HTTP_200_OK,
)
async def upload_media(
    guard: GuardDep,
    media_service: MediaServiceDep,
    avatar: Optional[UploadFile] = File(None),
    background: Optional[UploadFile] = File(None),
):
    """Upload avatar and/or background images. Returns the MinIO URLs for both files."""
    urls = await media_service.upload_media(guard, avatar, background)
    return UploadURLs(avatar_url=urls["avatar_url"], background_url=urls["background_url"])


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
