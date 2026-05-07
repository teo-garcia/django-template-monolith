"""Django settings module. Reads all values from Pydantic AppSettings (env-validated)."""

import os
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, unquote, urlparse

from app.config.env import get_settings

_settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent.parent


def _database_from_url(database_url: str) -> dict[str, Any]:
    parsed = urlparse(database_url)

    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ValueError("DATABASE_URL must use a postgres:// or postgresql:// scheme")
    if not parsed.hostname:
        raise ValueError("DATABASE_URL must include a host")
    if not parsed.path or parsed.path == "/":
        raise ValueError("DATABASE_URL must include a database name")

    config: dict[str, Any] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(parsed.path.lstrip("/")),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname,
        "PORT": str(parsed.port or ""),
        "CONN_MAX_AGE": 600,
    }

    if parsed.query:
        config["OPTIONS"] = dict(parse_qsl(parsed.query, keep_blank_values=True))

    return config


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
if _settings.metrics_enabled:
    MIDDLEWARE.append("app.shared.metrics.middleware.MetricsMiddleware")

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

DATABASES = {"default": _database_from_url(_settings.database_url)}

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
