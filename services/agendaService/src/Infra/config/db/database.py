import os
def get_database_url() -> str:
    return os.getenv("AGENDA_DATABASE_URL", "postgresql://postgres:password@agenda-postgres:5432/agendadb")


def get_sqlite_path(database_url: str | None = None):
    raise RuntimeError("agendaService now uses Postgres; use get_database_url instead")
