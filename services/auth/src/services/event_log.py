import json

import psycopg2

from ..config import get_settings


def init_db() -> None:
    settings = get_settings()
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
    settings = get_settings()
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
