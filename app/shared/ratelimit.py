from collections.abc import Callable
from typing import cast

from django.conf import settings
from django.http import HttpRequest
from django_ratelimit.decorators import ratelimit


def _api_rate(_group: str, _request: HttpRequest) -> str:
    return str(settings.RATELIMIT_RATE)


def api_ratelimit[**P, R](view_func: Callable[P, R]) -> Callable[P, R]:
    limited = ratelimit(group="api", key="ip", rate=_api_rate, block=True)(view_func)
    return cast(Callable[P, R], limited)
