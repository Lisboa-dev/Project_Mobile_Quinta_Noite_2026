from typing import Any, Protocol

from src.modules.agenda.aplication.dtos.useCase.query import ListDaysQuery, ListQuery


class EntityQueryRepositoryPort(Protocol):
    async def get_by_id(self, entity_id: str) -> dict[str, Any] | None:
        ...

    async def _list(self, query: ListQuery) -> list[dict[str, Any]]:
        ...


class AppointmentQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    async def list_by_patient(self, patient_id: str, query: ListQuery) -> list[dict[str, Any]]:
        ...

    async def list_by_doctor(self, doctor_id: str, query: ListQuery) -> list[dict[str, Any]]:
        ...


class ClinicQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    pass


class DoctorQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    pass


class PatientQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    pass


class RoomQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    async def get_admin_detail(self, room_id: str) -> dict[str, Any] | None:
        ...

    async def list_admin_detailed(self, query: ListQuery) -> list[dict[str, Any]]:
        ...


class AppointmentTypeQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    pass


class RuleQueryRepositoryPort(EntityQueryRepositoryPort, Protocol):
    async def admin_context(self) -> dict[str, Any]:
        ...

    async def detail(self, rule_id: str) -> dict[str, Any] | None:
        ...

    async def list_rules(self, query: ListQuery) -> list[dict[str, Any]]:
        ...


class CalendarQueryRepositoryPort(Protocol):
    async def get_by_id(self, day_id: str) -> dict[str, Any] | None:
        ...

    async def list_days(self, query: ListDaysQuery) -> list[dict[str, Any]]:
        ...

    async def list_month_for_front(self, year: int, month: int) -> list[dict[str, Any]]:
        ...
