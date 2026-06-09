import json
import os
from contextlib import contextmanager
from typing import Any, Generator

import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv(
    "NOTIFICATION_DATABASE_URL",
    "postgresql://postgres:password@notification-postgres:5432/notificationdb",
).replace("+psycopg2", "")


@contextmanager
def connect() -> Generator:
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
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    channel TEXT NOT NULL DEFAULT 'bell',
                    link TEXT,
                    read BOOLEAN NOT NULL DEFAULT FALSE,
                    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS ix_notifications_user_created
                    ON notifications (user_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS ix_notifications_user_read
                    ON notifications (user_id, read);

                CREATE TABLE IF NOT EXISTS notification_event_logs (
                    id BIGSERIAL PRIMARY KEY,
                    event_name TEXT NOT NULL,
                    routing_key TEXT NOT NULL,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )


class NotificationRepository:
    def create(self, notification: dict[str, Any]) -> dict[str, Any]:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO notifications (id, user_id, title, message, channel, link, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                    RETURNING id, user_id, title, message, channel, link, read, metadata, created_at
                    """,
                    (
                        notification["id"],
                        notification["user_id"],
                        notification["title"],
                        notification["message"],
                        notification.get("channel", "bell"),
                        notification.get("link"),
                        json.dumps(notification.get("metadata") or {}, default=str),
                    ),
                )
                return dict(cursor.fetchone())

    def list_by_user(self, user_id: str, limit: int = 50, unread_only: bool = False) -> list[dict[str, Any]]:
        with connect() as connection:
            with connection.cursor() as cursor:
                if unread_only:
                    cursor.execute(
                        """
                        SELECT id, user_id, title, message, channel, link, read, metadata, created_at
                        FROM notifications
                        WHERE user_id = %s AND read = false
                        ORDER BY created_at DESC
                        LIMIT %s
                        """,
                        (user_id, limit),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT id, user_id, title, message, channel, link, read, metadata, created_at
                        FROM notifications
                        WHERE user_id = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                        """,
                        (user_id, limit),
                    )
                return [dict(row) for row in cursor.fetchall()]

    def get(self, notification_id: str) -> dict[str, Any] | None:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, user_id, title, message, channel, link, read, metadata, created_at
                    FROM notifications
                    WHERE id = %s
                    """,
                    (notification_id,),
                )
                row = cursor.fetchone()
                return dict(row) if row else None

    def mark_read(self, notification_id: str) -> dict[str, Any] | None:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE notifications
                    SET read = true
                    WHERE id = %s
                    RETURNING id, user_id, title, message, channel, link, read, metadata, created_at
                    """,
                    (notification_id,),
                )
                row = cursor.fetchone()
                return dict(row) if row else None

    def count_unread(self, user_id: str) -> int:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM notifications
                    WHERE user_id = %s AND read = false
                    """,
                    (user_id,),
                )
                row = cursor.fetchone()
                return int(row["total"])


def log_event(event_name: str, routing_key: str, payload: dict[str, Any]) -> None:
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO notification_event_logs (event_name, routing_key, payload)
                VALUES (%s, %s, %s::jsonb)
                """,
                (event_name, routing_key, json.dumps(payload, default=str)),
            )
