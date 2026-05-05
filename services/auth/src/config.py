import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # 🌐 App
    APP_NAME: str = "auth-service"
    PORT: int = int(os.getenv("PORT", 8000))
    ENV: str = os.getenv("ENV", "development")

    # 🔐 Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "changeme")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    TOKEN_EXPIRE_MINUTES: int = int(os.getenv("TOKEN_EXPIRE_MINUTES", 60))

    # 🔗 Serviços externos
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://user-service")

    # ⚡ HTTP Client
    HTTP_TIMEOUT: float = float(os.getenv("HTTP_TIMEOUT", 3.0))

    # 🗄️ Banco (se usar depois)
    # DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")


@lru_cache
def get_settings() -> Settings:
    return Settings()