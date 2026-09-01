from datetime import UTC, datetime

import structlog
from django.db import connection
from django.http import JsonResponse

from app.config.env import get_settings
from app.shared.redis.client import get_redis_client

logger = structlog.get_logger("health")
settings = get_settings()

# Shared portfolio health contract, identical to the frontend templates'
# `lib/health.ts` and the Nest, Adonis, Gin and FastAPI backends:
#   {status, timestamp, version, checks{name: "up"|"down"}}
CHECK_UP = "up"
CHECK_DOWN = "down"


def _resolve_status(checks: dict[str, str]) -> str:
    """Every check up -> ok, some up -> degraded, none up -> down."""
    states = list(checks.values())

    if not states or all(state == CHECK_UP for state in states):
        return "ok"
    if all(state == CHECK_DOWN for state in states):
        return "down"
    return "degraded"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _run_checks() -> dict[str, str]:
    checks: dict[str, str] = {}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = CHECK_UP
    except Exception:
        logger.warning("health_check_failed", service="database")
        checks["database"] = CHECK_DOWN

    try:
        redis = get_redis_client()
        redis.ping()
        checks["redis"] = CHECK_UP
    except Exception:
        logger.warning("health_check_failed", service="redis")
        checks["redis"] = CHECK_DOWN

    return checks


def _report() -> JsonResponse:
    """Shared by /health and /health/ready so the two can never disagree."""
    checks = _run_checks()
    status = _resolve_status(checks)

    # Degraded and down both drain the instance.
    status_code = 200 if status == "ok" else 503

    return JsonResponse(
        {
            "status": status,
            "timestamp": _now(),
            "version": settings.app_version,
            "checks": checks,
        },
        status=status_code,
    )


def service_info(request: object) -> JsonResponse:
    return JsonResponse(
        {
            "name": settings.app_name,
            "status": "ok",
            "version": settings.app_version,
        }
    )


def liveness(request: object) -> JsonResponse:
    """Liveness reports no checks: a dependency outage must not restart a
    healthy process."""
    return JsonResponse(
        {
            "status": "ok",
            "timestamp": _now(),
            "version": settings.app_version,
        }
    )


def readiness(request: object) -> JsonResponse:
    return _report()


def health(request: object) -> JsonResponse:
    return _report()
