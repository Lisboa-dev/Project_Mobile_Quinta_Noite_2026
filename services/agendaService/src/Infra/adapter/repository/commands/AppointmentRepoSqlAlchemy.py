
from src.infra.adapter.repository.base import SQLiteRepository
from src.infra.mapper.DomainMapper import AppointmentMapper
from src.modules.agenda.aplication.ports.repository.AppointmentRepositoryPort import AppointmentRepositoryPort


class AppointmentRepository(SQLiteRepository, AppointmentRepositoryPort):
    async def save(self, appointment, scheduler_id: str | None = None) -> None:
        appointment_id = self._entity_id(appointment)
        with self._db.connect() as connection:
            connection.execute(
                """
                INSERT INTO appointments (
                    id, scheduler_id, patient_id, doctor_id, room_id, date_id, status, data, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?::jsonb, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    scheduler_id = excluded.scheduler_id,
                    patient_id = excluded.patient_id,
                    doctor_id = excluded.doctor_id,
                    room_id = excluded.room_id,
                    date_id = excluded.date_id,
                    status = excluded.status,
                    data = excluded.data,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    appointment_id,
                    scheduler_id,
                    str(appointment.patient_id),
                    str(appointment.doctor_id),
                    str(appointment.room_id),
                    appointment.date,
                    str(getattr(appointment.status, "value", appointment.status)),
                    self._dump(appointment),
                ),
            )
        await self._cache_entity("appointments", appointment_id, appointment)

    async def update(self, appointment) -> None:
        await self.save(appointment)

    async def delete(self, appointment_id: str) -> None:
        self._delete_by_id("appointments", appointment_id)
        await self._invalidate_entity("appointments", appointment_id)

    async def get(self, appointment_id: str):
        return AppointmentMapper.toDomain(await self._fetch_json_cached("appointments", appointment_id))

    async def getAppointment(self, id: str):
        return await self.get(id)
