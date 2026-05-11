"""
Redis configuration for auth service.
"""

from typing import final

from pydantic import BaseModel, Field


@final
class RedisSettings(BaseModel):
    """Redis connection settings for token revocation storage."""

    url: str = Field(
        default="redis://:redis_secret@redis:6379/0",
        alias="URL",
        description="Redis connection URL",
    )
