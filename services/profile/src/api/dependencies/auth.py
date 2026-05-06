from fastapi import Header, HTTPException,status, Depends
from uuid import UUID
from typing import Annotated

def get_current_user(x_user_id: str = Header(..., description="ID user from KrakenD")) -> UUID:
    try:
        return UUID(x_user_id)
    except ValueError:
        # If the format is incorrect, we respond with a nice 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid user ID format in header 'X-User-ID'"
        )

GuardDep = Annotated[UUID, Depends(get_current_user)]


