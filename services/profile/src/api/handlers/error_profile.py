from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import ProfileNotFoundError, ProfileAlreadyExistsError


async def profile_not_found_handler(
    request: Request,
    exc: ProfileNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Profile not found."},
    )


async def profile_already_exists_handler(
    request: Request,
    exc: ProfileAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Profile already exists."},
    )

