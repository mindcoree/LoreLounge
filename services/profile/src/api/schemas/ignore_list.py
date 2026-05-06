from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from .profile import ProfileResponse

class IgnoreUserResponse(BaseModel):
    ignoreed_user_id: UUID = Field(
        ..., description="Unique identifier of the ignored user"
    )
    ignored_profile: Optional[ProfileResponse] = Field(
        None, description="Profile of the ignored user"
    )

    model_config = ConfigDict(from_attributes=True)
