from typing import Optional

from fastapi import APIRouter, File, UploadFile, status

from api.schemas.profile import UploadURLs
from api.dependencies import MediaServiceDep,GuardDep



router = APIRouter(tags=["Media endpoints"])  # /profile/

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
