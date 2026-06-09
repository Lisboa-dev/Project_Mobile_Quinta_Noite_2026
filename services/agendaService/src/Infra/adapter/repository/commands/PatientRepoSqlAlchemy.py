from src.infra.adapter.repository.base import SQLiteRepository
from src.infra.mapper.DomainMapper import PatientMapper


class PatientRepository(SQLiteRepository):
    async def save(self, patient) -> None:
        patient_id = self._entity_id(patient)
        with self._db.connect() as connection:
            connection.execute(
                """
                INSERT INTO patients (id, name, data, updated_at)
                VALUES (?, ?, ?::jsonb, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    data = excluded.data,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (patient_id, patient.name, self._dump(patient)),
            )
        await self._cache_entity("patients", patient_id, patient)

    async def update(self, patient) -> None:
        await self.save(patient)

    async def delete(self, patient_id: str) -> None:
        self._delete_by_id("patients", patient_id)
        await self._invalidate_entity("patients", patient_id)

    async def getPacient(self, patient_id: str):
        return PatientMapper.toDomain(await self._fetch_json_cached("patients", patient_id))

    async def getPatient(self, patient_id: str):
        return await self.getPacient(patient_id)
