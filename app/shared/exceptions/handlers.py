from typing import Any

import structlog
from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI
from ninja.errors import HttpError, ValidationError

logger = structlog.get_logger("exceptions")


def _error_body(status: int, error: str, detail: Any = None) -> dict[str, Any]:
    return {"statusCode": status, "error": error, "detail": detail}


def register_exception_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(HttpError)
    def http_error_handler(request: HttpRequest, exc: HttpError) -> HttpResponse:
        return api.create_response(
            request,
            _error_body(exc.status_code, type(exc).__name__, str(exc)),
            status=exc.status_code,
        )

    @api.exception_handler(ValidationError)
    def validation_error_handler(request: HttpRequest, exc: ValidationError) -> HttpResponse:
        return api.create_response(
            request,
            _error_body(422, "Validation Error", exc.errors),
            status=422,
        )

    @api.exception_handler(Exception)
    def unhandled_error_handler(request: HttpRequest, exc: Exception) -> HttpResponse:
        request_id = request.META.get("REQUEST_ID", "unknown")
        logger.error("unhandled_error", exc_info=exc, request_id=request_id)
        return api.create_response(
            request,
            _error_body(500, "Internal Server Error", "An unexpected error occurred."),
            status=500,
        )
