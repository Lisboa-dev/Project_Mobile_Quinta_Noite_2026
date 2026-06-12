import json
from dataclasses import asdict, is_dataclass
from typing import Any
from unicodedata import normalize

from src.infra.clients.rabbitmq import RabbitMQClient
from src.infra.config.settings import settings
from src.infra.handlers import (
    UserServiceDoctorCreatedHandler,
    UserServiceDoctorDeletedHandler,
    UserServicePatientCreatedHandler,
    UserServicePatientDeletedHandler,
)


def _event_name(payload: dict[str, Any]) -> str:
    event = payload.get("event") or payload.get("type") or payload.get("name") or ""
    return str(event).lower()


def _event_data(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data")
    return data if isinstance(data, dict) else payload


def _cargo(payload: dict[str, Any]) -> str:
    data = _event_data(payload)
    normalized = normalize("NFKD", str(data.get("cargo") or data.get("role") or "").strip().lower())
    return normalized.encode("ascii", "ignore").decode("ascii")


class UserServiceCreatedEventsConsumer:
    def __init__(
        self,
        rabbitmq: RabbitMQClient,
        doctor_created_handler: UserServiceDoctorCreatedHandler,
        patient_created_handler: UserServicePatientCreatedHandler,
        doctor_deleted_handler: UserServiceDoctorDeletedHandler,
        patient_deleted_handler: UserServicePatientDeletedHandler,
    ):
        self._rabbitmq = rabbitmq
        self._doctor_created_handler = doctor_created_handler
        self._patient_created_handler = patient_created_handler
        self._doctor_deleted_handler = doctor_deleted_handler
        self._patient_deleted_handler = patient_deleted_handler
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        await self._rabbitmq.consume(
            queue_name=settings.user_events_queue,
            routing_keys=[
                settings.user_doctor_created_routing_key,
                settings.user_patient_created_routing_key,
                settings.user_doctor_deleted_routing_key,
                settings.user_patient_deleted_routing_key,
            ],
            handler=self.handle_message,
        )
        self._started = True

    async def stop(self) -> None:
        self._started = False
        await self._rabbitmq.close()

    async def handle_message(self, message) -> None:
        async with message.process():
            payload = json.loads(message.body.decode("utf-8"))
            await self.handle_payload(payload, routing_key=message.routing_key)

    async def handle_payload(self, payload: dict[str, Any], routing_key: str | None = None) -> dict[str, Any]:
        event_name = _event_name(payload)
        route = (routing_key or event_name).lower()
        cargo = _cargo(payload)

        if route in {
            settings.user_doctor_created_routing_key,
            "mediccreatedevent",
            "doctorcreatedevent",
        } or (route == "usercreatedevent" and cargo in {"medico", "doctor", "medic"}):
            result = await self._doctor_created_handler.handle(payload)
        elif route in {
            settings.user_patient_created_routing_key,
            "pacientcreatedevent",
            "patientcreatedevent",
        } or (route == "usercreatedevent" and cargo in {"paciente", "patient", "pacient"}):
            result = await self._patient_created_handler.handle(payload)
        elif route in {
            settings.user_doctor_deleted_routing_key,
            "medicdeletedevent",
            "doctordeletedevent",
        } or (route == "userdeletedevent" and cargo in {"medico", "doctor", "medic"}):
            result = await self._doctor_deleted_handler.handle(payload)
        elif route in {
            settings.user_patient_deleted_routing_key,
            "pacientdeletedevent",
            "patientdeletedevent",
        } or (route == "userdeletedevent" and cargo in {"paciente", "patient", "pacient"}):
            result = await self._patient_deleted_handler.handle(payload)
        else:
            return {"handled": False, "reason": f"ignored event route={route}"}

        return asdict(result) if is_dataclass(result) else dict(result)
