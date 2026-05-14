from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI

from app.config.env import get_settings
from app.modules.tasks.router import router as tasks_router
from app.shared.exceptions.handlers import register_exception_handlers
from app.shared.health.views import health, liveness, readiness, service_info
from app.shared.metrics.views import metrics_view

settings = get_settings()

api = NinjaAPI(
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
