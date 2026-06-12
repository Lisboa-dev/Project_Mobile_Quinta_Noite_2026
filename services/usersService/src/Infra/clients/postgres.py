from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.infra.clients.base import ClientHealth
from src.infra.config.settings import settings


class Base(DeclarativeBase):
    pass


class PostgresClient:
    def __init__(self, url: str | None = None):
        self.url = (url or settings.database_url).replace("+asyncpg", "+psycopg2")
        self.engine = create_engine(self.url, pool_pre_ping=True, future=True)
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        db = self.session_factory()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def ping(self) -> ClientHealth:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return ClientHealth("postgres", True)
        except Exception as exc:
            return ClientHealth("postgres", False, str(exc))


postgres_client = PostgresClient()
