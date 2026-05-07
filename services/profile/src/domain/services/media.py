from uuid import UUID
import asyncio
from typing import Optional
from fastapi import UploadFile

from config.settings import settings
from infrastructure.storage.minio_client import upload_file_to_minio
from domain.exceptions.media import MediaFormatError, MediaSizeError


class MediaService:
    """Service for handling media uploads to MinIO."""

    @staticmethod
    async def validate_image(upload: UploadFile) -> None:
        """Validate image file before upload.
        
        Raises:
            MediaFormatError: If MIME type is not allowed.
            MediaSizeError: If file size exceeds the limit.
        """
        # 1. Check MIME type
        if not upload.content_type or upload.content_type not in settings.storage.allowed_mime_types:
            raise MediaFormatError(upload.content_type or "unknown")
        
        # 2. Check file size
        if upload.size and upload.size > settings.storage.max_file_size_bytes:
            raise MediaSizeError(settings.storage.max_file_size_mb)

    async def upload_avatar(
        self,
        user_id: UUID,
        avatar: UploadFile,
    ) -> str:
        """Upload avatar to MinIO and return URL."""
        await self.validate_image(avatar)
        new_url = await upload_file_to_minio(user_id, avatar, file_type="avatar")
        return new_url

    async def upload_background(
        self,
        user_id: UUID,
        background: UploadFile,
    ) -> str:
        """Upload background to MinIO and return URL."""
        await self.validate_image(background)
        new_url = await upload_file_to_minio(user_id, background, file_type="background")
        return new_url

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

        if avatar and background:
            # If both files are provided, we can upload them concurrently for better performance
            avatar_url, background_url = await asyncio.gather(
                self.upload_avatar(user_id, avatar),
                self.upload_background(user_id, background),
            )
        else:
            if avatar:
                avatar_url = await self.upload_avatar(user_id, avatar)
            if background:
                background_url = await self.upload_background(user_id, background)
                
        return {
            "avatar_url": avatar_url,
            "background_url": background_url,
        }
