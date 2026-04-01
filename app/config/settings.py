"""Django settings module. Reads all values from Pydantic AppSettings (env-validated)."""

import os
from pathlib import Path

from app.config.env import get_settings

_settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = _settings.secret_key
DEBUG = _settings.debug
ALLOWED_HOSTS = _settings.allowed_hosts_list

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "app.modules.tasks",
]

MIDDLEWARE = [
    "app.shared.middleware.request_id.RequestIdMiddleware",
    "app.shared.middleware.security_headers.SecurityHeadersMiddleware",
    "app.shared.middleware.logging_mw.LoggingMiddleware",
]

if _settings.cors_enabled:
    MIDDLEWARE.insert(0, "app.shared.middleware.cors.CorsMiddleware")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]

ROOT_URLCONF = "app.config.urls"
ASGI_APPLICATION = "app.config.asgi.application"
WSGI_APPLICATION = "app.config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _settings.database_url.rsplit("/", 1)[-1],
        "USER": _settings.database_url.split("://")[1].split(":")[0],
        "PASSWORD": _settings.database_url.split(":")[2].split("@")[0],
        "HOST": _settings.database_url.split("@")[1].split(":")[0],
        "PORT": _settings.database_url.split(":")[-1].split("/")[0],
        "CONN_MAX_AGE": 600,
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": _settings.redis_url,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Structlog logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": _settings.log_level.upper(),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": _settings.log_level.upper(),
            "propagate": False,
        },
    },
}

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")
