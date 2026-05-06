from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class ProfileCreate(BaseModel):
    name: str = Field(
        ..., max_length=100, description="Unique user nickname"
    )
    bio: Optional[str] = Field(
        None, max_length=500, description="Short user biography"
    )
    avatar_url: Optional[str] = Field(
        None, description="User avatar URL"
    )
    background_url: Optional[str] = Field(
        None, description="User profile background URL"
    )


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(
        None, max_length=100, description="Unique user nickname"
    )
    bio: Optional[str] = Field(
        None, max_length=500, description="Short user biography"
    )
    avatar_url: Optional[str] = Field(
        None, description="User avatar URL"
    )
    background_url: Optional[str] = Field(
        None, description="User profile background URL"
    )


class ProfileResponse(BaseModel):
    id: int = Field(..., description="Internal profile ID")
    user_id: UUID = Field(
        ..., description="Unique user identifier"
    )
    name: str = Field(..., max_length=100, description="Unique user nickname")
    bio: Optional[str] = Field(
        None, max_length=500, description="Short user biography"
    )
    avatar_url: Optional[str] = Field(
        None, description="User avatar URL"
    )
    background_url: Optional[str] = Field(
        None, description="User profile background URL"
    )
    created_at: datetime = Field(..., description="The timestamp when the profile was created.")
    updated_at: datetime = Field(..., description="The timestamp when the profile was last updated.")

    model_config = ConfigDict(from_attributes=True)


class UploadURLs(BaseModel):
    avatar_url: Optional[str] = Field(None, description="Uploaded avatar URL")
    background_url: Optional[str] = Field(None, description="Uploaded background URL")

    model_config = ConfigDict(from_attributes=True)
