from contextlib import contextmanager
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from src.infra.config.settings import settings


class CursorAdapter:
    def __init__(self, cursor):
        self._cursor = cursor

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    def execute(self, sql: str, params: tuple[Any, ...] | None = None):
        return self._cursor.execute(sql.replace("?", "%s"), params)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __iter__(self):
        return iter(self._cursor.fetchall())


class ConnectionAdapter:
    def __init__(self, connection):
        self._connection = connection
        self._cursor = connection.cursor(cursor_factory=RealDictCursor)

    def execute(self, sql: str, params: tuple[Any, ...] | None = None) -> CursorAdapter:
        self._cursor.execute(sql.replace("?", "%s"), params)
        return CursorAdapter(self._cursor)

    def executescript(self, script: str) -> None:
        self._cursor.execute(script)

    def commit(self) -> None:
        self._connection.commit()

    def rollback(self) -> None:
        self._connection.rollback()

    def close(self) -> None:
        self._cursor.close()
        self._connection.close()


class Database:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.database_url.replace("+asyncpg", "")

    @contextmanager
    def connect(self):
        connection = ConnectionAdapter(psycopg2.connect(self.database_url))
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()


database = Database()
