import structlog
from django.db import connection
from django.http import JsonResponse

from app.config.env import get_settings
from app.shared.redis.client import get_redis_client

logger = structlog.get_logger("health")
settings = get_settings()


def service_info(request: object) -> JsonResponse:
    return JsonResponse(
        {
            "name": settings.app_name,
            "status": "ok",
            "version": settings.app_version,
        }
    )


def liveness(request: object) -> JsonResponse:
    return JsonResponse({"status": "ok"})


def readiness(request: object) -> JsonResponse:
    checks: dict[str, str] = {}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception:
        logger.warning("health_check_failed", service="database")
        checks["database"] = "error"

    try:
        redis = get_redis_client()
        redis.ping()
        checks["redis"] = "ok"
    except Exception:
        logger.warning("health_check_failed", service="redis")
        checks["redis"] = "error"

    is_healthy = all(value == "ok" for value in checks.values())
    status_code = 200 if is_healthy else 503
    status = "ok" if is_healthy else "error"
    return JsonResponse({"status": status, "checks": checks}, status=status_code)


def health(request: object) -> JsonResponse:
    checks: dict[str, str] = {}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception:
        logger.warning("health_check_failed", service="database")
        checks["database"] = "error"

    try:
        redis = get_redis_client()
        redis.ping()
        checks["redis"] = "ok"
    except Exception:
        logger.warning("health_check_failed", service="redis")
        checks["redis"] = "error"

    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    status_code = 200 if overall == "ok" else 503
    return JsonResponse({"status": overall, "checks": checks}, status=status_code)
