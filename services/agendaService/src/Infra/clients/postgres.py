from urllib.parse import urlparse

from src.infra.clients.base import ClientHealth
from src.infra.config.settings import settings


class PostgresClient:
    def __init__(self, database_url: str | None = None):
        self._database_url = self._normalize(database_url or settings.database_url)

    def _normalize(self, url: str) -> str:
        if url.startswith("postgresql+asyncpg://"):
            return "postgresql://" + url.removeprefix("postgresql+asyncpg://")
        return url

    def connect(self):
        import psycopg2  # type: ignore[import-untyped]

        return psycopg2.connect(self._database_url, connect_timeout=settings.client_timeout_seconds)

    def ping(self) -> ClientHealth:
        try:
            parsed = urlparse(self._database_url)
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            return ClientHealth(
                "postgres",
                True,
                metadata={"host": parsed.hostname, "database": parsed.path.lstrip("/")},
            )
        except Exception as exc:
            return ClientHealth("postgres", False, str(exc))
