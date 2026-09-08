import atexit
import os

from django.core.wsgi import get_wsgi_application

from app.config.env import get_settings
from app.shared.logging.config import configure_logging
from app.shared.telemetry import configure_telemetry, shutdown_telemetry

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")

settings = get_settings()
configure_logging(settings.log_level, json_output=settings.log_json)
configure_telemetry(settings)
atexit.register(shutdown_telemetry)

application = get_wsgi_application()
