from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from app.config.env import get_settings

_settings = get_settings()


class CorsMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.method == "OPTIONS":
            response = HttpResponse()
            response.status_code = 204
        else:
            response = self.get_response(request)

        response["Access-Control-Allow-Origin"] = _settings.cors_origin
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Request-ID"
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Max-Age"] = "86400"
        return response
