from pydantic import BaseModel, Field


class Pagination(BaseModel):
    limit: int = Field(10, gt=0)
    offset: int = Field(0, ge=0)

