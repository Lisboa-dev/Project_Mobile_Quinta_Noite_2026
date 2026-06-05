import json
from uuid import uuid4

from src.infra.database import connect, log_event


class PostgresBellNotificationRepository:
    def save(self, data) -> dict:
        notification = {
            "id": str(uuid4()),
            "user_id": data.user_id,
            "title": data.title,
            "message": data.message,
            "link": data.link,
            "read": False,
            "metadata": data.metadata or {},
        }
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO notifications (id, user_id, title, message, link, read, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                    """,
                    (
                        notification["id"],
                        notification["user_id"],
                        notification["title"],
                        notification["message"],
                        notification["link"],
                        notification["read"],
                        json.dumps(notification["metadata"]),
                    ),
                )
        log_event("NotificationCreated", "notification.created", notification)
        return notification

    def list_by_user(self, user_id: str) -> list[dict]:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
                return [dict(row) for row in cursor.fetchall()]

    def find_by_id(self, notification_id: str) -> dict | None:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM notifications WHERE id = %s", (notification_id,))
                row = cursor.fetchone()
                return dict(row) if row else None

    def mark_as_read(self, notification_id: str) -> dict | None:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE notifications SET read = TRUE WHERE id = %s RETURNING *",
                    (notification_id,),
                )
                row = cursor.fetchone()
                notification = dict(row) if row else None
        if notification:
            log_event("NotificationRead", "notification.read", notification)
        return notification

    def mark_all_as_read(self, user_id: str) -> None:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE notifications SET read = TRUE WHERE user_id = %s", (user_id,))
        log_event("NotificationsReadAll", "notification.read_all", {"user_id": user_id})

    def count_unread(self, user_id: str) -> int:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS count FROM notifications WHERE user_id = %s AND read = FALSE", (user_id,))
                return int(cursor.fetchone()["count"])
