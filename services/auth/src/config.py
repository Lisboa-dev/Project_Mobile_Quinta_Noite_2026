import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


def _load_env_files() -> None:
    auth_root = Path(__file__).resolve().parents[1]
    project_root = auth_root.parents[1] if len(auth_root.parents) > 1 else auth_root

    load_dotenv(project_root / ".env", override=False)
    load_dotenv(auth_root / ".env", override=True)


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value not in (None, "") else default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value not in (None, "") else default


_load_env_files()


@dataclass(frozen=True)
class Settings:
    APP_NAME: str = os.getenv("AUTH_APP_NAME", "auth-service")
    PORT: int = _get_int("AUTH_PORT", _get_int("PORT", 8000))
    ENV: str = os.getenv("ENV", "development")
    AUTH_DATABASE_URL: str = os.getenv(
        "AUTH_DATABASE_URL",
        "postgresql://postgres:password@auth-postgres:5432/authdb",
    )

    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-env")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    TOKEN_EXPIRE_MINUTES: int = _get_int("TOKEN_EXPIRE_MINUTES", 60)
    REFRESH_TOKEN_EXPIRE_DAYS: int = _get_int("REFRESH_TOKEN_EXPIRE_DAYS", 7)

    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://users-service:8000")
    USER_LOOKUP_PATH: str = os.getenv("USER_LOOKUP_PATH", "/user/")
    HTTP_TIMEOUT: float = _get_float("HTTP_TIMEOUT", 5.0)

    OPENFGA_ENABLED: bool = os.getenv("OPENFGA_ENABLED", "true").lower() == "true"
    OPENFGA_API_URL: str = os.getenv("OPENFGA_API_URL", "http://openfga:8080")
    OPENFGA_STORE_NAME: str = os.getenv("OPENFGA_STORE_NAME", "agendamento-medico")
    OPENFGA_AUTHZ_FAIL_OPEN: bool = os.getenv("OPENFGA_AUTHZ_FAIL_OPEN", "false").lower() == "true"

    AUTH_DEV_USER_ID: str = os.getenv("AUTH_DEV_USER_ID", "1")
    AUTH_DEV_USER_EMAIL: str = os.getenv("AUTH_DEV_USER_EMAIL", "admin@example.com")
    AUTH_DEV_USER_NAME: str = os.getenv("AUTH_DEV_USER_NAME", "admin")
    AUTH_DEV_USER_PASSWORD: str = os.getenv("AUTH_DEV_USER_PASSWORD", "Admin123!")
    AUTH_DEV_USER_ROLE: str = os.getenv("AUTH_DEV_USER_ROLE", "admin")


@lru_cache
def get_settings() -> Settings:
    return Settings()
