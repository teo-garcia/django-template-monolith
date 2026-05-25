import uuid
from collections.abc import Callable

import structlog
from django.http import HttpRequest, HttpResponse
from opentelemetry import trace


class RequestIdMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.META["REQUEST_ID"] = request_id

        span_context = trace.get_current_span().get_span_context()
        trace_fields = (
            {
                "trace_id": format(span_context.trace_id, "032x"),
                "span_id": format(span_context.span_id, "016x"),
            }
            if span_context.is_valid
            else {}
        )

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id, **trace_fields)

        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        return response
