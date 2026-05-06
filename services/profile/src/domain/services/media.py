from uuid import UUID
from typing import Optional
from fastapi import UploadFile

from infrastructure.storage.minio_client import upload_file_to_minio


class MediaService:
    """Service for handling media uploads to MinIO."""

    async def upload_avatar(self, user_id: UUID, avatar: UploadFile) -> str:
        """Upload avatar to MinIO and return URL."""
        return await upload_file_to_minio(user_id, avatar, file_type="avatar")

    async def upload_background(self, user_id: UUID, background: UploadFile) -> str:
        """Upload background to MinIO and return URL."""
        return await upload_file_to_minio(user_id, background, file_type="background")

    async def upload_media(
        self,
        user_id: UUID,
        avatar: Optional[UploadFile] = None,
        background: Optional[UploadFile] = None,
    ) -> dict[str, Optional[str]]:
        """Upload avatar and/or background to MinIO and return their URLs.
        
        Returns:
            dict with 'avatar_url' and 'background_url' keys (None if not provided)
        """
        avatar_url: Optional[str] = None
        background_url: Optional[str] = None

        if avatar is not None:
            avatar_url = await self.upload_avatar(user_id, avatar)

        if background is not None:
            background_url = await self.upload_background(user_id, background)

        return {
            "avatar_url": avatar_url,
            "background_url": background_url,
        }
