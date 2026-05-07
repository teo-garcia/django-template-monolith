import time
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from prometheus_client import Counter, Histogram

UNKNOWN_ROUTE = "__unknown__"

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "route"],
)


def _route_label(request: HttpRequest) -> str:
    resolver_match = getattr(request, "resolver_match", None)
    route = getattr(resolver_match, "route", None)
    if not isinstance(route, str):
        return UNKNOWN_ROUTE
    return f"/{route}" if route else "/"


class MetricsMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()
        response = self.get_response(request)
        duration = time.perf_counter() - start

        route = _route_label(request)
        REQUEST_COUNT.labels(method=request.method, route=route, status=str(response.status_code)).inc()
        REQUEST_DURATION.labels(method=request.method, route=route).observe(duration)

        return response
