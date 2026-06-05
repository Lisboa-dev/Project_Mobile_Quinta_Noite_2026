import json
import os
from contextlib import contextmanager
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv(
    "ANALYTIC_DATABASE_URL",
    "postgresql://postgres:password@analytic-postgres:5432/analyticdb",
)


@contextmanager
def connect():
    connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
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
                    service_name TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    routing_key TEXT NOT NULL,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS analytic_events (
                    id BIGSERIAL PRIMARY KEY,
                    event_name TEXT NOT NULL,
                    routing_key TEXT NOT NULL,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            cursor.execute("SELECT COUNT(*) AS count FROM analytic_events")
            if int(cursor.fetchone()["count"]) == 0:
                seed_events = [
                    ("AppointmentCreatedEvent", "agenda.appointment.created", {"data": {"doctor_id": "doctor-1", "status": "scheduled"}}),
                    ("AppointmentCreatedEvent", "agenda.appointment.created", {"data": {"doctor_id": "doctor-1", "status": "scheduled"}}),
                    ("AppointmentUpdatedEvent", "agenda.appointment.updated", {"data": {"doctor_id": "doctor-1", "status": "finished"}}),
                    ("AppointmentDeletedEvent", "agenda.appointment.deleted", {"data": {"doctor_id": "doctor-1", "status": "canceled"}}),
                    ("UserCreatedEvent", "users.doctor.created", {"data": {"cargo": "MEDICO"}}),
                    ("PacientCreatedEvent", "users.patient.created", {"data": {}}),
                ]
                for event_name, routing_key, payload in seed_events:
                    cursor.execute(
                        "INSERT INTO analytic_events (event_name, routing_key, payload) VALUES (%s, %s, %s::jsonb)",
                        (event_name, routing_key, json.dumps(payload)),
                    )


def record_event(event_name: str, routing_key: str, payload: dict[str, Any]) -> None:
    with connect() as connection:
        with connection.cursor() as cursor:
            body = json.dumps(payload, default=str)
            cursor.execute(
                "INSERT INTO analytic_events (event_name, routing_key, payload) VALUES (%s, %s, %s::jsonb)",
                (event_name, routing_key, body),
            )
            cursor.execute(
                """
                INSERT INTO event_logs (service_name, event_name, routing_key, payload)
                VALUES (%s, %s, %s, %s::jsonb)
                """,
                ("analytic-service", event_name, routing_key, body),
            )
