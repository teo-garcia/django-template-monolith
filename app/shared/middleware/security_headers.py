from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "0",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

_DOCS_PATHS = frozenset({"/api/docs", "/api/docs/openapi.json"})


class SecurityHeadersMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        is_docs = request.path in _DOCS_PATHS
        for header, value in SECURITY_HEADERS.items():
            if is_docs and header == "Content-Security-Policy":
                continue
            if header not in response:
                response[header] = value
        return response
