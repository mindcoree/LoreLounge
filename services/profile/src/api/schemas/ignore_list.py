from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from .profile import ProfileResponse

class IgnoreUserResponse(BaseModel):
    ignored_user_id: UUID = Field(
        ..., description="Unique identifier of the ignored user"
    )
    ignored_profile: ProfileResponse | None = Field(
        None, description="Profile of the ignored user"
    )

    model_config = ConfigDict(from_attributes=True)


class IgnoreListPageResponse(BaseModel):
    items: list[IgnoreUserResponse] = Field(default_factory=list)
    total: int = Field(..., ge=0)
    limit: int = Field(..., gt=0)
    offset: int = Field(..., ge=0)
