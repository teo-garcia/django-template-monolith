import os

from django.core.wsgi import get_wsgi_application

from app.config.env import get_settings
from app.shared.telemetry import configure_telemetry

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")

configure_telemetry(get_settings())

application = get_wsgi_application()
