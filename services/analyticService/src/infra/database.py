import json
from contextlib import contextmanager
from typing import Any, Generator

import psycopg2
from psycopg2.extras import RealDictCursor

from src.infra.settings import settings


@contextmanager
def connect() -> Generator:
    connection = psycopg2.connect(settings.database_url, cursor_factory=RealDictCursor)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS event_logs (
                    id BIGSERIAL PRIMARY KEY,
                    source_service TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    routing_key TEXT NOT NULL,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS ix_event_logs_route_created
                    ON event_logs (routing_key, created_at DESC);
                CREATE INDEX IF NOT EXISTS ix_event_logs_event_created
                    ON event_logs (event_name, created_at DESC);
                """
            )


class EventLogRepository:
    def save(self, payload: dict[str, Any], routing_key: str) -> dict[str, Any]:
        event_name = str(payload.get("event") or payload.get("type") or routing_key)
        source_service = self._source_from_route(routing_key)
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO event_logs (source_service, event_name, routing_key, payload)
                    VALUES (%s, %s, %s, %s::jsonb)
                    RETURNING id, source_service, event_name, routing_key, payload, created_at
                    """,
                    (source_service, event_name, routing_key, json.dumps(payload, default=str)),
                )
                return dict(cursor.fetchone())

    def list_recent(self, limit: int = 100) -> list[dict[str, Any]]:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, source_service, event_name, routing_key, payload, created_at
                    FROM event_logs
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                return [dict(row) for row in cursor.fetchall()]

    def count_by_source(self) -> list[dict[str, Any]]:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT source_service, COUNT(*) AS total
                    FROM event_logs
                    GROUP BY source_service
                    ORDER BY source_service
                    """
                )
                return [dict(row) for row in cursor.fetchall()]

    def _source_from_route(self, routing_key: str) -> str:
        if routing_key.startswith("users."):
            return "users-service"
        if routing_key.startswith("agenda."):
            return "agenda-service"
        return "unknown"
