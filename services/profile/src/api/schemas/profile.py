from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID

class Profile(BaseModel):
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
    user_id: UUID = Field(
        ..., description="Unique user identifier"
    )

    model_config = ConfigDict(from_attributes=True)