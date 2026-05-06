from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    SelfIgnoreError,
    UserAlreadyIgnoredError,
    UserNotInIgnoreListError,
)


async def self_ignore_handler(
    request: Request,
    exc: SelfIgnoreError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "You cannot add yourself to the ignore list."},
    )


async def user_already_ignored_handler(
    request: Request,
    exc: UserAlreadyIgnoredError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "User is already in your ignore list."},
    )


async def user_not_in_ignore_list_handler(
    request: Request,
    exc: UserNotInIgnoreListError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "This user is not in your ignore list."},
    )
