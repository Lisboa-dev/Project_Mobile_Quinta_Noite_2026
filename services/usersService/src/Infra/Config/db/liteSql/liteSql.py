from contextlib import contextmanager
from typing import Generator

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.infra.clients.postgres import Base, postgres_client


engine = postgres_client.engine
SessionLocal = postgres_client.session_factory


@contextmanager
def get_query() -> Generator[Session, None, None]:
    with postgres_client.session() as session:
        yield session


get_command = get_query


def _postgres_table_exists(connection, table_name: str) -> bool:
    return bool(
        connection.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = current_schema()
                      AND table_name = :table_name
                )
                """
            ),
            {"table_name": table_name},
        ).scalar()
    )


def _postgres_column_is_uuid(connection, table_name: str, column_name: str) -> bool:
    return (
        connection.execute(
            text(
                """
                SELECT udt_name
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = :table_name
                  AND column_name = :column_name
                """
            ),
            {"table_name": table_name, "column_name": column_name},
        ).scalar()
        == "uuid"
    )


def _normalize_uuid_schema() -> None:
    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        has_users = _postgres_table_exists(connection, "users")
        has_doctors = _postgres_table_exists(connection, "doctors")
        has_event_logs = _postgres_table_exists(connection, "event_logs")

        if has_users and not _postgres_column_is_uuid(connection, "users", "id"):
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS id_uuid uuid"))
            connection.execute(
                text(
                    """
                    UPDATE users
                    SET id_uuid = CASE
                        WHEN id::text ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
                        THEN id::text::uuid
                        ELSE gen_random_uuid()
                    END
                    WHERE id_uuid IS NULL
                    """
                )
            )

        if has_doctors:
            if not _postgres_column_is_uuid(connection, "doctors", "id"):
                connection.execute(text("ALTER TABLE doctors ADD COLUMN IF NOT EXISTS id_uuid uuid"))
                connection.execute(
                    text(
                        """
                        UPDATE doctors
                        SET id_uuid = CASE
                            WHEN id::text ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
                            THEN id::text::uuid
                            ELSE gen_random_uuid()
                        END
                        WHERE id_uuid IS NULL
                        """
                    )
                )
            if has_users and not _postgres_column_is_uuid(connection, "doctors", "user_id"):
                connection.execute(text("ALTER TABLE doctors ADD COLUMN IF NOT EXISTS user_id_uuid uuid"))
                connection.execute(
                    text(
                        """
                        UPDATE doctors d
                        SET user_id_uuid = u.id_uuid
                        FROM users u
                        WHERE d.user_id::text = u.id::text
                          AND d.user_id_uuid IS NULL
                        """
                    )
                )

        if has_event_logs and not _postgres_column_is_uuid(connection, "event_logs", "id"):
            connection.execute(text("ALTER TABLE event_logs ADD COLUMN IF NOT EXISTS id_uuid uuid"))
            connection.execute(
                text(
                    """
                    UPDATE event_logs
                    SET id_uuid = CASE
                        WHEN id::text ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
                        THEN id::text::uuid
                        ELSE gen_random_uuid()
                    END
                    WHERE id_uuid IS NULL
                    """
                )
            )

        if has_doctors and has_users and not _postgres_column_is_uuid(connection, "doctors", "user_id"):
            connection.execute(text("ALTER TABLE doctors DROP CONSTRAINT IF EXISTS doctors_user_id_fkey"))
            connection.execute(text("ALTER TABLE doctors DROP CONSTRAINT IF EXISTS doctors_user_id_key"))
            connection.execute(text("ALTER TABLE doctors DROP COLUMN user_id"))
            connection.execute(text("ALTER TABLE doctors RENAME COLUMN user_id_uuid TO user_id"))
            connection.execute(text("ALTER TABLE doctors ALTER COLUMN user_id SET NOT NULL"))
            connection.execute(text("ALTER TABLE doctors ADD CONSTRAINT doctors_user_id_key UNIQUE (user_id)"))

        if has_doctors and not _postgres_column_is_uuid(connection, "doctors", "id"):
            connection.execute(text("ALTER TABLE doctors DROP CONSTRAINT IF EXISTS doctors_pkey"))
            connection.execute(text("ALTER TABLE doctors DROP COLUMN id"))
            connection.execute(text("ALTER TABLE doctors RENAME COLUMN id_uuid TO id"))
            connection.execute(text("ALTER TABLE doctors ALTER COLUMN id SET NOT NULL"))
            connection.execute(text("ALTER TABLE doctors ADD CONSTRAINT doctors_pkey PRIMARY KEY (id)"))

        if has_users and not _postgres_column_is_uuid(connection, "users", "id"):
            if has_doctors:
                connection.execute(text("ALTER TABLE doctors DROP CONSTRAINT IF EXISTS doctors_user_id_fkey"))
            connection.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_pkey"))
            connection.execute(text("ALTER TABLE users DROP COLUMN id"))
            connection.execute(text("ALTER TABLE users RENAME COLUMN id_uuid TO id"))
            connection.execute(text("ALTER TABLE users ALTER COLUMN id SET NOT NULL"))
            connection.execute(text("ALTER TABLE users ADD CONSTRAINT users_pkey PRIMARY KEY (id)"))

        if has_doctors and has_users:
            connection.execute(text("ALTER TABLE doctors DROP CONSTRAINT IF EXISTS doctors_user_id_fkey"))
            connection.execute(
                text(
                    """
                    ALTER TABLE doctors
                    ADD CONSTRAINT doctors_user_id_fkey
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    """
                )
            )

        if has_event_logs and not _postgres_column_is_uuid(connection, "event_logs", "id"):
            connection.execute(text("ALTER TABLE event_logs DROP CONSTRAINT IF EXISTS event_logs_pkey"))
            connection.execute(text("ALTER TABLE event_logs DROP COLUMN id"))
            connection.execute(text("ALTER TABLE event_logs RENAME COLUMN id_uuid TO id"))
            connection.execute(text("ALTER TABLE event_logs ALTER COLUMN id SET NOT NULL"))
            connection.execute(text("ALTER TABLE event_logs ADD CONSTRAINT event_logs_pkey PRIMARY KEY (id)"))


def init_db() -> None:
    from src.infra.models.sqlAlchemy.UserSqlSchamy import Doctor, EventLog, Usuario  # noqa: F401

    _normalize_uuid_schema()
    Base.metadata.create_all(bind=engine)
