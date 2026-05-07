from django.urls import path
from django.views.generic import RedirectView

from app.config.env import get_settings
from app.main import api
from app.shared.health.views import health, liveness, readiness, service_info
from app.shared.metrics.views import metrics_view

settings = get_settings()

urlpatterns = [
    path("", service_info),
    path(
        "docs",
        RedirectView.as_view(url=f"{settings.api_prefix.rstrip('/')}/docs", permanent=False),
    ),
    path("health/", health),
    path("health/live", liveness),
    path("health/ready", readiness),
    path(settings.api_prefix.strip("/") + "/", api.urls),
]

if settings.metrics_enabled:
    urlpatterns.append(path("metrics", metrics_view))
