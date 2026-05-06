from fastapi import Header, HTTPException,status, Depends
from uuid import UUID
from typing import Annotated

def get_current_user(x_user_id: str = Header(..., description="ID user from KrakenD")) -> UUID:
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID format in header 'X-User-ID'")
    return UUID(x_user_id)


GuardDep = Annotated[UUID, Depends(get_current_user)]


