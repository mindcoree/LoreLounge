from fastapi import Request, status
from fastapi.responses import JSONResponse

from domain.exceptions import (
    RoleRequestAlreadyExistsError,
    RoleRequestNotFoundError,
    RoleRequestAlreadyProcessedError,
)


async def role_request_already_exists_handler(
    request: Request,
    exc: RoleRequestAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def role_request_not_found_handler(
    request: Request,
    exc: RoleRequestNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def role_request_already_processed_handler(
    request: Request,
    exc: RoleRequestAlreadyProcessedError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )
