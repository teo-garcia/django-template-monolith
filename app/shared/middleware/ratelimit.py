import time
from collections.abc import Callable
from typing import TypedDict, cast

from django.http import HttpRequest, HttpResponse


class RateLimitUsage(TypedDict):
    count: int
    limit: int
    should_limit: bool
    time_left: int


class RateLimitHeadersMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        usage = cast(RateLimitUsage | None, request.META.get("API_RATELIMIT_USAGE"))

        if usage is not None:
            response["X-RateLimit-Limit"] = str(usage["limit"])
            response["X-RateLimit-Remaining"] = str(max(usage["limit"] - usage["count"], 0))
            response["X-RateLimit-Reset"] = str(int(time.time()) + max(usage["time_left"], 0))

        return response
