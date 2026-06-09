from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from src.infra.clients.postgres import Base, postgres_client


engine = postgres_client.engine
SessionLocal = postgres_client.session_factory


@contextmanager
def get_query() -> Generator[Session, None, None]:
    with postgres_client.session() as session:
        yield session


get_command = get_query


def init_db() -> None:
    from src.infra.models.sqlAlchemy.UserSqlSchamy import EventLog, Usuario  # noqa: F401

    Base.metadata.create_all(bind=engine)
