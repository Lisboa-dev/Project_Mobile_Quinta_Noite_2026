from src.infra.adapter.repository.base import SQLiteRepository


class DoctorRepository(SQLiteRepository):
    async def save(self, doctor) -> None:
        doctor_id = self._entity_id(doctor)
        data = self._load(self._dump(doctor))
        with self._db.connect() as connection:
            connection.execute(
                """
                INSERT INTO doctors (id, name, data, updated_at)
                VALUES (?, ?, ?::jsonb, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    data = excluded.data,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (doctor_id, data.get("name", ""), self._dump(doctor)),
            )
        await self._cache_entity("doctors", doctor_id, doctor)

    async def update(self, doctor) -> None:
        await self.save(doctor)

    async def delete(self, doctor_id: str) -> None:
        self._delete_by_id("doctors", doctor_id)
        await self._invalidate_entity("doctors", doctor_id)

    async def get(self, doctor_id: str):
        return await self._fetch_json_cached("doctors", doctor_id)

    async def getDoctor(self, doctor_id: str):
        return await self.get(doctor_id)

    async def GetDoctorGenericRules(self) -> list:
        with self._db.connect() as connection:
            rows = connection.execute(
                "SELECT data FROM rules WHERE target_type = 'DOCTOR' AND target IS NULL"
            ).fetchall()
            return [self._load(row["data"]) for row in rows]
