"""
Storage configuration for media files and MinIO settings.
"""

from typing import final

from pydantic import BaseModel, Field


@final
class MinioSettings(BaseModel):
    """MinIO settings for media storage."""

    endpoint: str = Field("localhost:9000", alias="ENDPOINT")
    access_key: str = Field("admin", alias="ACCESS_KEY")
    secret_key: str = Field("SuperSecret123!", alias="SECRET_KEY")
    use_ssl: bool = Field(False, alias="USE_SSL")
    bucket_name: str = Field("lorelounge-media", alias="BUCKET_NAME")
    base_path: str = Field("profile", alias="BASE_PATH")


@final
class StorageSettings(BaseModel):
    """MinIO and media storage validation settings."""

    allowed_mime_types: list[str] = Field(
        default=["image/jpeg", "image/png", "image/webp", "image/gif"],
        alias="ALLOWED_MIME_TYPES",
        description="List of allowed MIME types for image uploads"
    )
    max_file_size_mb: int = Field(
        default=5,
        alias="MAX_FILE_SIZE_MB",
        description="Maximum file size in MB"
    )

    @property
    def max_file_size_bytes(self) -> int:
        """Calculate max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

