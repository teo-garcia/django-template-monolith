import os

from django.core.asgi import get_asgi_application
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware

from app.config.env import get_settings
from app.shared.telemetry import configure_telemetry

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")

configure_telemetry(get_settings())

application = OpenTelemetryMiddleware(get_asgi_application())
