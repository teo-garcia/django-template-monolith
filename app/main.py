from typing import Any

from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI
from ninja.openapi.schema import OpenAPISchema

from app.config.env import get_settings
from app.modules.tasks.router import router as tasks_router
from app.shared.exceptions.handlers import register_exception_handlers
from app.shared.health.views import health, liveness, readiness, service_info
from app.shared.metrics.views import metrics_view
from app.shared.openapi.envelope import apply_success_envelope

settings = get_settings()


class EnvelopeNinjaAPI(NinjaAPI):
    """Ninja API whose OpenAPI document describes the success envelope applied
    by `ResponseEnvelopeMiddleware`."""

    def get_openapi_schema(
        self,
        path_prefix: str | None = None,
        path_params: dict[str, Any] | None = None,
    ) -> OpenAPISchema:
        schema = super().get_openapi_schema(path_prefix=path_prefix, path_params=path_params)
        apply_success_envelope(schema)
        return schema


api = EnvelopeNinjaAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
)

register_exception_handlers(api)


@api.get("/", tags=["service"])
def get_service_info(request: HttpRequest) -> HttpResponse:
    return service_info(request)


@api.get("/health/live", tags=["health"])
def get_liveness(request: HttpRequest) -> HttpResponse:
    return liveness(request)


@api.get("/health/ready", tags=["health"])
def get_readiness(request: HttpRequest) -> HttpResponse:
    return readiness(request)


@api.get("/health", tags=["health"])
def get_health(request: HttpRequest) -> HttpResponse:
    return health(request)


if settings.metrics_enabled:

    @api.get("/metrics", tags=["metrics"])
    def get_metrics(request: HttpRequest) -> HttpResponse:
        return metrics_view(request)


api.add_router(f"{settings.api_prefix.rstrip('/')}/tasks", tasks_router)
