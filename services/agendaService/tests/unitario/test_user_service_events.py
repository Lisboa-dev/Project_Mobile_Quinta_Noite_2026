import asyncio

from src.infra.adapter.Messaging.rabbitMQ.userServiceConsumers import UserServiceCreatedEventsConsumer
from src.infra.handlers.UserServiceEventHandlers import (
    UserServiceDoctorCreatedHandler,
    UserServiceDoctorDeletedHandler,
    UserServicePatientCreatedHandler,
    UserServicePatientDeletedHandler,
)
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO


class FakeCreateUseCase:
    def __init__(self, resource: str):
        self.resource = resource
        self.commands = []

    async def execute(self, command):
        self.commands.append(command)
        return UseCaseOutputDTO.ok(
            use_case=f"create_{self.resource}",
            action="create",
            resource=self.resource,
            resource_id=getattr(command, "id", getattr(command, "id_extern", None)),
            triggered_by_id=command.triggered_by_id,
        )


class FakeDeleteUseCase:
    def __init__(self, resource: str):
        self.resource = resource
        self.calls = []

    async def execute(self, entity_id, triggered_by_id=None):
        self.calls.append((entity_id, triggered_by_id))
        return UseCaseOutputDTO.ok(
            use_case=f"delete_{self.resource}",
            action="delete",
            resource=self.resource,
            resource_id=entity_id,
            triggered_by_id=triggered_by_id,
        )


def _consumer():
    doctor_create = FakeCreateUseCase("doctor")
    patient_create = FakeCreateUseCase("patient")
    doctor_delete = FakeDeleteUseCase("doctor")
    patient_delete = FakeDeleteUseCase("patient")

    consumer = UserServiceCreatedEventsConsumer(
        rabbitmq=None,
        doctor_created_handler=UserServiceDoctorCreatedHandler(doctor_create),
        patient_created_handler=UserServicePatientCreatedHandler(patient_create),
        doctor_deleted_handler=UserServiceDoctorDeletedHandler(doctor_delete),
        patient_deleted_handler=UserServicePatientDeletedHandler(patient_delete),
    )

    return consumer, doctor_create, patient_create, doctor_delete, patient_delete


def test_users_service_medic_created_event_creates_agenda_doctor():
    async def run():
        consumer, doctor_create, *_ = _consumer()

        result = await consumer.handle_payload(
            {
                "event": "MedicCreatedEvent",
                "data": {
                    "id": "medic-1",
                    "userName": "dra.ana",
                    "name": "Dra. Ana",
                    "email": "ana@clinica.local",
                    "cargo": "MEDICO",
                    "crm": "CRM-123",
                    "triggered_by_id": "admin-1",
                },
            }
        )

        assert result["handled"] is True
        assert result["entity"] == "doctor"
        assert result["external_id"] == "medic-1"
        assert doctor_create.commands[0].id_extern == "medic-1"
        assert doctor_create.commands[0].name == "dra.ana"
        assert doctor_create.commands[0].triggered_by_id == "admin-1"

    asyncio.run(run())


def test_users_service_pacient_created_event_creates_agenda_patient():
    async def run():
        consumer, _, patient_create, *_ = _consumer()

        result = await consumer.handle_payload(
            {
                "event": "PacientCreatedEvent",
                "data": {
                    "id": "patient-1",
                    "userName": "joao.paciente",
                    "name": "Joao Paciente",
                    "email": "joao@example.com",
                    "cargo": "PACIENTE",
                    "cpf": "00000000000",
                    "triggered_by_id": "admin-1",
                },
            }
        )

        assert result["handled"] is True
        assert result["entity"] == "patient"
        assert result["external_id"] == "patient-1"
        assert patient_create.commands[0].id == "patient-1"
        assert patient_create.commands[0].name == "joao.paciente"
        assert patient_create.commands[0].triggered_by_id == "admin-1"

    asyncio.run(run())


def test_users_service_delete_events_delete_agenda_doctor_and_patient():
    async def run():
        consumer, _, _, doctor_delete, patient_delete = _consumer()

        doctor_result = await consumer.handle_payload(
            {
                "event": "MedicDeletedEvent",
                "data": {
                    "id": "medic-1",
                    "cargo": "MEDICO",
                    "triggered_by_id": "admin-1",
                },
            }
        )
        patient_result = await consumer.handle_payload(
            {
                "event": "PacientDeletedEvent",
                "data": {
                    "id": "patient-1",
                    "cargo": "PACIENTE",
                    "triggered_by_id": "admin-1",
                },
            }
        )

        assert doctor_result["handled"] is True
        assert patient_result["handled"] is True
        assert doctor_delete.calls == [("medic-1", "admin-1")]
        assert patient_delete.calls == [("patient-1", "admin-1")]

    asyncio.run(run())


def test_generic_user_created_event_routes_by_cargo():
    async def run():
        consumer, _, patient_create, *_ = _consumer()

        result = await consumer.handle_payload(
            {
                "event": "UserCreatedEvent",
                "data": {
                    "id": "patient-1",
                    "userName": "joao.paciente",
                    "cargo": "PACIENTE",
                    "triggered_by_id": "admin-1",
                },
            }
        )

        assert result["handled"] is True
        assert result["entity"] == "patient"
        assert patient_create.commands[0].id == "patient-1"

    asyncio.run(run())
