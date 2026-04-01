import redis

from app.config.env import get_settings

_settings = get_settings()

_redis_client = redis.Redis(
    host=_settings.redis_host,
    port=_settings.redis_port,
    password=_settings.redis_password or None,
    decode_responses=True,
)


def get_redis_client() -> redis.Redis:
    return _redis_client
