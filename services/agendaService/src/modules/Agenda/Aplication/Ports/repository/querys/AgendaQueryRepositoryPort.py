from typing import Any, Protocol

from src.modules.agenda.aplication.dtos.useCase.query import ListDaysQuery, ListQuery


class EntityQueryRepositoryPort(Protocol):
    async def get_by_id(self, entity_id: str) -> dict[str, Any] | None:
        ...

    async def list(self, query: ListQuery) -> list[dict[str, Any]]:
        ...


class AppointmentQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    pass


class ClinicQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    pass


class DoctorQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    pass


class PatientQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    pass


class RoomQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    pass


class RuleQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    pass


class CalendarQueryRepositoryPort(Protocol):
    async def get_by_id(self, day_id: str) -> dict[str, Any] | None:
        ...

    async def list(self, query: ListDaysQuery) -> list[dict[str, Any]]:
        ...
