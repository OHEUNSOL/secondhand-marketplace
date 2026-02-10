from datetime import datetime, timezone

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.services.errors import ServiceError


def _error_code_from_status(status_code: int) -> str:
    if status_code == 400:
        return "BAD_REQUEST"
    if status_code == 401:
        return "UNAUTHORIZED"
    if status_code == 403:
        return "FORBIDDEN"
    if status_code == 404:
        return "NOT_FOUND"
    if status_code == 409:
        return "CONFLICT"
    if status_code == 422:
        return "VALIDATION_ERROR"
    return "INTERNAL_SERVER_ERROR" if status_code >= 500 else "ERROR"


def build_error_body(
    *,
    status_code: int,
    message: str,
    path: str,
    details: object | None = None,
    code: str | None = None,
) -> dict[str, object]:
    return {
        "success": False,
        "error": {
            "code": code or _error_code_from_status(status_code),
            "message": message,
            "details": details,
            "path": path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


def service_error_response(request: Request, exc: ServiceError) -> JSONResponse:
    body = build_error_body(
        status_code=exc.status_code,
        message=exc.message,
        path=request.url.path,
    )
    return JSONResponse(status_code=exc.status_code, content=body)


def http_error_response(request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    details = None if isinstance(exc.detail, str) else exc.detail
    body = build_error_body(
        status_code=exc.status_code,
        message=message,
        details=details,
        path=request.url.path,
    )
    return JSONResponse(status_code=exc.status_code, content=body)


def validation_error_response(request: Request, exc: RequestValidationError) -> JSONResponse:
    body = build_error_body(
        status_code=422,
        message="Validation failed",
        details=exc.errors(),
        path=request.url.path,
        code="VALIDATION_ERROR",
    )
    return JSONResponse(status_code=422, content=body)


def internal_error_response(request: Request) -> JSONResponse:
    body = build_error_body(
        status_code=500,
        message="Internal server error",
        path=request.url.path,
        code="INTERNAL_SERVER_ERROR",
    )
    return JSONResponse(status_code=500, content=body)

