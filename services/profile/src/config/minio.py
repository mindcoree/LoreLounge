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

  