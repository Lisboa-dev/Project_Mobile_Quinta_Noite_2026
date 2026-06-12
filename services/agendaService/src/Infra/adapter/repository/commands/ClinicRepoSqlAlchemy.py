from src.infra.adapter.repository.base import SQLiteRepository
from src.infra.mapper.DomainMapper import ClinicMapper


class ClinicRepository(SQLiteRepository):
    async def save(self, clinic) -> None:
        clinic_id = self._entity_id(clinic)
        with self._db.connect() as connection:
            connection.execute(
                """
                INSERT INTO clinics (id, name, data, updated_at)
                VALUES (?, ?, ?::jsonb, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    data = excluded.data,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (clinic_id, clinic.name, self._dump(clinic)),
            )
        await self._cache_entity("clinics", clinic_id, clinic)

    async def update(self, clinic) -> None:
        await self.save(clinic)

    async def delete(self, id: str) -> None:
        self._delete_by_id("clinics", id)
        await self._invalidate_entity("clinics", id)

    async def getClinic(self, clinic_id: str | None = None):
        with self._db.connect() as connection:
            if clinic_id:
                return ClinicMapper.toDomain(await self._fetch_json_cached("clinics", clinic_id))
            else:
                row = connection.execute(
                    "SELECT data FROM clinics ORDER BY created_at DESC LIMIT 1"
                ).fetchone()
            return ClinicMapper.toDomain(self._load(row["data"])) if row else None
