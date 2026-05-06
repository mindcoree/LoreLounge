from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID


class Profile(BaseModel):
    name: str = Field(
        ..., max_length=100, description="Уникальный никнейм пользователя"
    )
    bio: Optional[str] = Field(
        None, max_length=500, description="Краткая биография пользователя"
    )
    avatar_url: Optional[str] = Field(None, description="URL аватара пользователя")
    backgroud_url: Optional[str] = Field(
        None, description="URL фона профиля пользователя"
    )


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(
        None, max_length=100, description="Уникальный никнейм пользователя"
    )
    bio: Optional[str] = Field(
        None, max_length=500, description="Краткая биография пользователя"
    )
    avatar_url: Optional[str] = Field(None, description="URL аватара пользователя")
    backgroud_url: Optional[str] = Field(
        None, description="URL фона профиля пользователя"
    )


class ProfileResponse(BaseModel):
    user_id: UUID = Field(..., description="Уникальный идентификатор пользователя")

    model_config = ConfigDict(from_attributes=True)


class IgnoreUserResponse(BaseModel):
    ignoreed_user_id: UUID = Field(
        ..., description="Уникальный идентификатор игнорируемого пользователя"
    )
    ignored_profile: Optional[ProfileResponse] = Field(
        None, description="Профиль игнорируемого пользователя"
    )

    model_config = ConfigDict(from_attributes=True)
