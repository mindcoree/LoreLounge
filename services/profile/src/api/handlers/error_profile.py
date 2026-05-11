from fastapi import Request, status
from fastapi.responses import JSONResponse

from domain.exceptions import (
    ProfileConflictError,
    ProfileNameTakenError,
    ProfileNotFoundError,
)


async def profile_not_found_handler(
    request: Request,
    exc: ProfileNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Profile not found."},
    )


async def profile_name_taken_handler(
    request: Request,
    exc: ProfileNameTakenError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": f"Profile name '{exc.name}' is already taken."},
    )


async def profile_conflict_handler(
    request: Request,
    exc: ProfileConflictError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Profile conflict."},
    )

