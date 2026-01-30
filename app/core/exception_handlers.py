"""Global exception handlers for FastAPI."""

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


async def ai_service_exception_handler(
    request: Request, exc: AIServiceException
) -> JSONResponse:
    """
    Handle custom AI service exceptions.

    Args:
        request: The FastAPI request
        exc: The AI service exception

    Returns:
        JSONResponse with error details
    """
    logger.error(
        f"AI Service Exception: {exc.error_code} - {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "error_code": exc.error_code,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "status": exc.status_code,
            }
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation errors.

    Args:
        request: The FastAPI request
        exc: The validation error

    Returns:
        JSONResponse with validation error details
    """
    logger.warning(
        f"Validation error on {request.method} {request.url.path}",
        extra={"errors": exc.errors()},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "status": 422,
                "details": exc.errors(),
            }
        },
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handle HTTP exceptions.

    Args:
        request: The FastAPI request
        exc: The HTTP exception

    Returns:
        JSONResponse with error details
    """
    logger.error(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "http_error",
                "message": exc.detail,
                "status": exc.status_code,
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        request: The FastAPI request
        exc: The exception

    Returns:
        JSONResponse with generic error message
    """
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected error occurred. Please try again later.",
                "status": 500,
            }
        },
    )
