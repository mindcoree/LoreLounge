from pydantic import BaseModel, Field


class ApiAuthPrefix(BaseModel):
    prefix: str = "/auth"
