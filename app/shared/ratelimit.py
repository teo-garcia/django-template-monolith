from collections.abc import Callable
from functools import wraps
from typing import cast

from django.conf import settings
from django.http import HttpRequest
from django_ratelimit.core import get_usage
from django_ratelimit.decorators import ratelimit


def _api_rate(_group: str, _request: HttpRequest) -> str:
    return str(settings.RATELIMIT_RATE)


def api_ratelimit[**P, R](view_func: Callable[P, R]) -> Callable[P, R]:
    limited = ratelimit(group="api", key="ip", rate=_api_rate, block=True)(view_func)

    @wraps(view_func)
    def with_usage(request: HttpRequest, *args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return cast(R, limited(request, *args, **kwargs))
        finally:
            request.META["API_RATELIMIT_USAGE"] = get_usage(
                request,
                group="api",
                key="ip",
                rate=_api_rate,
                increment=False,
            )

    return cast(Callable[P, R], with_usage)
