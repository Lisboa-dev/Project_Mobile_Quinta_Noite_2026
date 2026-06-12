import json
import os

try:
    import psycopg2
except ImportError:  # pragma: no cover - exercised only in minimal test environments
    psycopg2 = None

from ..config import get_settings


def _skip_persistent_log() -> bool:
    return (
        os.getenv("TEST_USE_MOCK_DATA", "true").lower() in {"1", "true", "yes", "on"}
        or get_settings().ENV == "test"
        or psycopg2 is None
    )


def init_db() -> None:
    if _skip_persistent_log():
        return

    settings = get_settings()
    if psycopg2 is None:
        raise Exception("psycopg2 not found")
    connection = psycopg2.connect(settings.AUTH_DATABASE_URL)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS event_logs (
                    id BIGSERIAL PRIMARY KEY,
                    service_name TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    routing_key TEXT NOT NULL,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        connection.commit()
    finally:
        connection.close()


def log_event(event_name: str, routing_key: str, payload: dict) -> None:
    if _skip_persistent_log():
        return

    settings = get_settings()
    if psycopg2 is None:
        raise Exception("psycopg2 not found")
    connection = psycopg2.connect(settings.AUTH_DATABASE_URL)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO event_logs (service_name, event_name, routing_key, payload)
                VALUES (%s, %s, %s, %s::jsonb)
                """,
                ("auth-service", event_name, routing_key, json.dumps(payload, default=str)),
            )
        connection.commit()
    finally:
        connection.close()
