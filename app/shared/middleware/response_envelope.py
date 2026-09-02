import json
from collections.abc import Callable
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse

from app.config.env import get_settings

# Paths served verbatim. Health and metrics are parsed by orchestrators and
# Prometheus, and the docs routes serve HTML/the OpenAPI document, so none of
# them may be wrapped. Mirrors the skip lists in the other backend templates.
UNWRAPPED_EXACT = frozenset({"/metrics", "/docs", "/openapi.json"})
UNWRAPPED_PREFIXES = ("/health", "/docs/")


def _is_unwrapped(path: str) -> bool:
    return path in UNWRAPPED_EXACT or path.startswith(UNWRAPPED_PREFIXES)


class ResponseEnvelopeMiddleware:
    """Wraps successful responses in the shared portfolio success envelope:

    {success, statusCode, timestamp, path, method, data, meta{requestId, version, duration}}

    Failures are left alone: `app/shared/exceptions/handlers.py` already emits
    the matching error envelope.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        self.settings = get_settings()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        started = perf_counter()
        response = self.get_response(request)

        if _is_unwrapped(request.path):
            return response

        # 204 must not carry a body, and >= 400 is already an error envelope.
        if response.status_code == 204 or response.status_code >= 400:
            return response

        if response.headers.get("Content-Type", "").split(";")[0] != "application/json":
            return response

        if getattr(response, "streaming", False) or not response.content:
            return response

        try:
            data: Any = json.loads(response.content)
        except json.JSONDecodeError:
            return response

        # Never double-wrap a handler that already returned an envelope.
        if isinstance(data, dict) and "success" in data:
            return response

        query = request.META.get("QUERY_STRING", "")
        path = f"{request.path}?{query}" if query else request.path

        meta: dict[str, Any] = {}
        request_id = request.META.get("REQUEST_ID")
        if request_id:
            meta["requestId"] = request_id
        meta["version"] = self.settings.app_version
        meta["duration"] = round((perf_counter() - started) * 1000)

        enveloped = JsonResponse(
            {
                "success": True,
                "statusCode": response.status_code,
                "timestamp": datetime.now(UTC).isoformat(),
                "path": path,
                "method": request.method,
                "data": data,
                "meta": meta,
            },
            status=response.status_code,
        )

        # Preserve headers set by outer middleware (request id, security, CORS).
        for key, value in response.items():
            if key.lower() not in {"content-type", "content-length"}:
                enveloped[key] = value

        return enveloped
