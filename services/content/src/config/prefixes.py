from pydantic import BaseModel, Field



class ApiContentPrefix(BaseModel):
	prefix: str = "/content"
