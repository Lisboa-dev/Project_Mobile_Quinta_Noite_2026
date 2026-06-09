import os
from dataclasses import dataclass


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    service_name: str = os.getenv("USERS_SERVICE_NAME", "users-service")
    database_url: str = os.getenv(
        "USERS_DATABASE_URL",
        "postgresql+psycopg2://postgres:password@users-postgres:5432/usersdb",
    ).replace("+asyncpg", "+psycopg2")
    redis_url: str = os.getenv("REDIS_URL", "redis://users-redis:6379/0")
    rabbitmq_url: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    user_events_exchange: str = os.getenv("USER_EVENTS_EXCHANGE", "users.events")
    prometheus_url: str = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
    client_timeout_seconds: int = int(os.getenv("USERS_CLIENT_TIMEOUT_SECONDS", "3"))
    redis_events_channel: str = os.getenv("USERS_REDIS_EVENTS_CHANNEL", "users.events")
    redis_cache_ttl_seconds: int = int(os.getenv("USERS_REDIS_CACHE_TTL_SECONDS", "300"))

    minio_endpoint_url: str = os.getenv("MINIO_ENDPOINT_URL", "http://minio:9000")
    minio_public_url: str = os.getenv("MINIO_PUBLIC_URL", minio_endpoint_url)
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "admin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "altere-esta-senha-forte")
    minio_bucket_name: str = os.getenv("MINIO_BUCKET_NAME", "user-profile-images")
    minio_secure: bool = _bool_env("MINIO_SECURE", False)

    profile_image_max_bytes: int = int(os.getenv("PROFILE_IMAGE_MAX_BYTES", str(5 * 1024 * 1024)))
    profile_image_allowed_types: frozenset[str] = frozenset(
        item.strip()
        for item in os.getenv("PROFILE_IMAGE_ALLOWED_TYPES", "image/jpeg,image/png,image/webp").split(",")
        if item.strip()
    )


settings = Settings()

MINIO_ENDPOINT_URL = settings.minio_endpoint_url
MINIO_PUBLIC_URL = settings.minio_public_url
MINIO_ACCESS_KEY = settings.minio_access_key
MINIO_SECRET_KEY = settings.minio_secret_key
MINIO_BUCKET_NAME = settings.minio_bucket_name
MINIO_SECURE = settings.minio_secure

PROFILE_IMAGE_MAX_BYTES = settings.profile_image_max_bytes
PROFILE_IMAGE_ALLOWED_TYPES = set(settings.profile_image_allowed_types)
