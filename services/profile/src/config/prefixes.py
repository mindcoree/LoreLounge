from pydantic import BaseModel, Field


class ApiUsersPrefix(BaseModel):
	prefix: str = "/users"


class ApiPrefix(BaseModel):
	prefix: str = "/api"
	users: ApiUsersPrefix = Field(default_factory=ApiUsersPrefix)