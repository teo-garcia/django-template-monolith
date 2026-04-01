from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Django Monolith Template"
    app_version: str = "1"
    debug: bool = False
    port: int = 8000
    api_prefix: str = "/api"
    secret_key: str = "change-me-in-production"  # noqa: S105
    allowed_hosts: str = "localhost,127.0.0.1,0.0.0.0"
    shutdown_timeout: int = 10

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/django_monolith"
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_ttl: int = 3600

    # Logging
    log_level: str = "info"
    log_json: bool = True

    # CORS
    cors_enabled: bool = True
    cors_origin: str = "http://localhost:3000"

    # Rate Limiting
    throttle_limit: str = "100/m"

    # Metrics
    metrics_enabled: bool = True

    @property
    def redis_url(self) -> str:
        password_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{password_part}{self.redis_host}:{self.redis_port}/0"

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [h.strip() for h in self.allowed_hosts.split(",")]


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
