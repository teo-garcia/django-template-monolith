import time
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)


class MetricsMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()
        response = self.get_response(request)
        duration = time.perf_counter() - start

        path = request.path
        REQUEST_COUNT.labels(method=request.method, path=path, status=response.status_code).inc()
        REQUEST_DURATION.labels(method=request.method, path=path).observe(duration)

        return response
