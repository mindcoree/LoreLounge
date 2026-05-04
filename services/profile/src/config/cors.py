from typing import final

from pydantic import BaseModel, Field


@final
class CORSSettings(BaseModel):
    """CORS configuration settings."""

    origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8080"]
    )
    allow_credentials: bool = True
    allow_methods: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    allow_headers: list[str] = Field(default_factory=lambda: ["*"])
