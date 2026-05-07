from fastapi import Request, status
from fastapi.responses import JSONResponse

from domain.exceptions import MediaFormatError, MediaSizeError

async def media_format_error_handler(
        request: Request,
        exc: MediaFormatError,
) -> JSONResponse:
    return JSONResponse(
        status_code = status.HTTP_400_BAD_REQUEST,
        content = {"detail": str(exc)},
    )

async def media_size_error_handler(
        request: Request,
        exc: MediaSizeError,
) -> JSONResponse:
    return JSONResponse(
        status_code = status.HTTP_413_CONTENT_TOO_LARGE,
        content = {"detail": str(exc)},
    )