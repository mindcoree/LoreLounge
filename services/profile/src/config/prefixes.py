from pydantic import BaseModel, Field



class ApiProfilePrefix(BaseModel):
	prefix: str = "/api/profile"
