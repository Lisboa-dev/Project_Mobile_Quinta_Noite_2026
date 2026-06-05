import json
from uuid import uuid4

from src.infra.database import connect, log_event


class PostgresEmailRepository:
    def save(self, data) -> dict:
        email = {
            "id": str(uuid4()),
            "to": data.to,
            "subject": data.subject,
            "body": data.body,
            "status": "pending",
            "metadata": data.metadata or {},
        }
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO emails (id, recipient, subject, body, status, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                    """,
                    (
                        email["id"],
                        email["to"],
                        email["subject"],
                        email["body"],
                        email["status"],
                        json.dumps(email["metadata"]),
                    ),
                )
        log_event("EmailQueued", "notification.email.queued", email)
        return email

    def update_status(self, email_id: str, status: str) -> dict | None:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE emails SET status = %s WHERE id = %s RETURNING *", (status, email_id))
                row = cursor.fetchone()
                return self._to_response(row) if row else None

    def list_all(self) -> list[dict]:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM emails ORDER BY created_at DESC")
                return [self._to_response(row) for row in cursor.fetchall()]

    def _to_response(self, row) -> dict:
        data = dict(row)
        data["to"] = data.pop("recipient")
        return data
