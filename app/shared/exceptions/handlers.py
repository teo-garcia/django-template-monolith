from datetime import UTC, datetime
from typing import Any

import structlog
from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI
from ninja.errors import HttpError, ValidationError

logger = structlog.get_logger("exceptions")


def _request_path(request: HttpRequest) -> str:
    return request.get_full_path()


def _api_error_body(
    request: HttpRequest,
    status: int,
    message: str,
    error: str,
    errors: Any = None,
) -> dict[str, Any]:
    request_id = request.META.get("REQUEST_ID")
    body = {
        "success": False,
        "statusCode": status,
        "timestamp": datetime.now(UTC).isoformat(),
        "path": _request_path(request),
        "method": request.method,
        "message": message,
        "error": error,
    }
    if request_id:
        body["meta"] = {"requestId": request_id}
    if errors is not None:
        body["errors"] = errors
    return body


def register_exception_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(HttpError)
    def http_error_handler(request: HttpRequest, exc: HttpError) -> HttpResponse:
        return api.create_response(
            request,
            _api_error_body(request, exc.status_code, str(exc), type(exc).__name__),
            status=exc.status_code,
        )

    @api.exception_handler(ValidationError)
    def validation_error_handler(request: HttpRequest, exc: ValidationError) -> HttpResponse:
        return api.create_response(
            request,
            _api_error_body(request, 422, "Validation failed", "ValidationError", exc.errors),
            status=422,
        )

    @api.exception_handler(Exception)
    def unhandled_error_handler(request: HttpRequest, exc: Exception) -> HttpResponse:
        request_id = request.META.get("REQUEST_ID", "unknown")
        logger.error("unhandled_error", exc_info=exc, request_id=request_id)
        return api.create_response(
            request,
            _api_error_body(
                request,
                500,
                "An unexpected error occurred.",
                "InternalServerError",
            ),
            status=500,
        )
