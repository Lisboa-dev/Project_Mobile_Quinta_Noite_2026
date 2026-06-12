from pathlib import Path

from src.infra.database import Database, database


class MigrationRunner:
    def __init__(self, db: Database = database, migrations_path: Path | None = None):
        self._db = db
        self._migrations_path = migrations_path or Path(__file__).resolve().parent

    def run(self) -> None:
        with self._db.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            applied = {
                row["version"]
                for row in connection.execute("SELECT version FROM schema_migrations")
            }
            for migration in sorted(self._migrations_path.glob("*.sql")):
                version = migration.name
                if version in applied:
                    continue
                connection.executescript(migration.read_text(encoding="utf-8"))
                connection.execute(
                    "INSERT INTO schema_migrations (version) VALUES (?)",
                    (version,),
                )
