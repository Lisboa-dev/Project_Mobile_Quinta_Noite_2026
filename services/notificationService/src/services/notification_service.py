from typing import Any
from uuid import uuid4

from src.infra.database import NotificationRepository, log_event
from src.infra.websocket import WebSocketHub


class NotificationDispatcher:
    def __init__(
        self,
        repository: NotificationRepository,
        hub: WebSocketHub | None = None,
        notifications_hub: WebSocketHub | None = None,
        events_hub: WebSocketHub | None = None,
    ) -> None:
        self.repository = repository
        self.notifications_hub = notifications_hub or hub or WebSocketHub()
        self.events_hub = events_hub or WebSocketHub()

    async def dispatch_event(self, payload: dict[str, Any], routing_key: str) -> None:
        event_name = str(payload.get("event") or payload.get("type") or routing_key)
        log_event(event_name, routing_key, payload)
        await self.events_hub.broadcast(
            {
                "event": "event.received",
                "routing_key": routing_key,
                "data": payload,
            }
        )

        notifications = self._build_notifications(payload, routing_key, event_name)
        if not notifications:
            return

        for notification in notifications:
            persisted = self.repository.create(notification)
            await self.notifications_hub.broadcast(
                {
                    "event": "notification.created",
                    "routing_key": routing_key,
                    "data": persisted,
                }
            )

    def _build_notifications(
        self,
        payload: dict[str, Any],
        routing_key: str,
        event_name: str,
    ) -> list[dict[str, Any]]:
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        specialized = self._build_feature_notifications(payload, data, routing_key, event_name)
        if specialized is not None:
            return specialized
        return [
            self._notification_for_recipient(payload, data, routing_key, event_name, user_id)
            for user_id in self._recipient_ids(data)
        ]

    def _build_feature_notifications(
        self,
        payload: dict[str, Any],
        data: dict[str, Any],
        routing_key: str,
        event_name: str,
    ) -> list[dict[str, Any]] | None:
        if routing_key == "agenda.appointment.created" or event_name == "agenda.appointment.created":
            notifications: list[dict[str, Any]] = []
            doctor_id = self._first_value(data, "doctor_id", "doctorId", "medic_id", "medicId")
            patient_id = self._first_value(data, "patient_id", "patientId")
            if doctor_id:
                notifications.append(
                    self._notification_for_recipient(
                        payload,
                        {
                            **data,
                            "title": "Nova consulta agendada",
                            "message": self._appointment_message(data, "Voce tem uma nova consulta agendada."),
                            "link": self._appointment_link(data),
                            "audience": "doctor",
                        },
                        routing_key,
                        event_name,
                        str(doctor_id),
                    )
                )
            if patient_id and self._is_return_appointment(data):
                notifications.append(
                    self._notification_for_recipient(
                        payload,
                        {
                            **data,
                            "title": "Re-consulta agendada",
                            "message": self._appointment_message(data, "Sua re-consulta foi agendada."),
                            "link": self._appointment_link(data),
                            "audience": "patient",
                        },
                        routing_key,
                        event_name,
                        str(patient_id),
                    )
                )
            return notifications

        if routing_key == "agenda.appointment.updated" or event_name == "agenda.appointment.updated":
            patient_id = self._first_value(data, "patient_id", "patientId")
            if not patient_id or not data.get("status"):
                return []
            return [
                self._notification_for_recipient(
                    payload,
                    {
                        **data,
                        "title": "Status da consulta alterado",
                        "message": self._appointment_message(
                            data,
                            f"Status da sua consulta alterado para {data.get('status')}.",
                        ),
                        "link": self._appointment_link(data),
                        "audience": "patient",
                    },
                    routing_key,
                    event_name,
                    str(patient_id),
                )
            ]

        if (
            routing_key == "users.doctor.created"
            or event_name == "MedicCreatedEvent"
            or (event_name == "UserCreatedEvent" and str(data.get("cargo") or "").upper() == "MEDICO")
        ):
            recipients = ["admin"]
            triggered_by_id = self._first_value(data, "triggered_by_id", "triggeredById")
            if triggered_by_id and str(triggered_by_id) not in recipients:
                recipients.append(str(triggered_by_id))
            doctor_name = data.get("name") or data.get("userName") or data.get("id")
            return [
                self._notification_for_recipient(
                    payload,
                    {
                        **data,
                        "title": "Novo medico criado",
                        "message": f"Medico {doctor_name} criado no sistema.",
                        "link": f"/admin/doctors/{data.get('id')}" if data.get("id") else "/admin/doctors",
                        "audience": "admin",
                    },
                    routing_key,
                    event_name,
                    recipient,
                )
                for recipient in recipients
            ]

        return None

    def _notification_for_recipient(
        self,
        payload: dict[str, Any],
        data: dict[str, Any],
        routing_key: str,
        event_name: str,
        user_id: str,
    ) -> dict[str, Any] | None:
        title = str(data.get("title") or payload.get("title") or self._title_from_event(event_name, routing_key))
        message = str(data.get("message") or payload.get("message") or f"Evento recebido: {event_name}")

        return {
            "id": str(uuid4()),
            "user_id": user_id,
            "title": title,
            "message": message,
            "channel": str(data.get("channel") or payload.get("channel") or "bell"),
            "link": data.get("link") or payload.get("link"),
            "metadata": {
                "event": event_name,
                "routing_key": routing_key,
                "audience": data.get("audience"),
                "appointment_id": data.get("appointment_id") or data.get("appointmentId"),
                "status": data.get("status"),
                "payload": payload,
            },
        }

    def _first_value(self, data: dict[str, Any], *fields: str) -> Any:
        for field in fields:
            value = data.get(field)
            if value:
                return value
        return None

    def _is_return_appointment(self, data: dict[str, Any]) -> bool:
        appointment_type = str(data.get("appointment_type") or data.get("appointmentType") or "").lower()
        return any(marker in appointment_type for marker in ("reconsulta", "re-consulta", "retorno", "return", "follow"))

    def _appointment_link(self, data: dict[str, Any]) -> str | None:
        appointment_id = data.get("appointment_id") or data.get("appointmentId")
        return f"/agenda/appointments/{appointment_id}" if appointment_id else data.get("link")

    def _appointment_message(self, data: dict[str, Any], fallback: str) -> str:
        date = data.get("date")
        time = data.get("time")
        if date and time:
            return f"{fallback} Data: {date}, horario: {time}."
        return fallback

    def _recipient_ids(self, data: dict[str, Any]) -> list[str]:
        recipients: list[str] = []
        for field in (
            "user_id",
            "userId",
            "patient_id",
            "patientId",
            "doctor_id",
            "doctorId",
            "medic_id",
            "medicId",
            "scheduler_id",
            "schedulerId",
            "id",
        ):
            value = data.get(field)
            if value and str(value) not in recipients:
                recipients.append(str(value))
        return recipients

    def _title_from_event(self, event_name: str, routing_key: str) -> str:
        text = event_name or routing_key
        text = text.replace("_", " ").replace(".", " ").replace("-", " ")
        return " ".join(part.capitalize() for part in text.split())


class NotificationQueryService:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    def list_by_user(self, user_id: str, limit: int = 50, unread_only: bool = False) -> list[dict[str, Any]]:
        return self.repository.list_by_user(user_id=user_id, limit=limit, unread_only=unread_only)

    def mark_read(self, notification_id: str) -> dict[str, Any] | None:
        return self.repository.mark_read(notification_id)

    def count_unread(self, user_id: str) -> int:
        return self.repository.count_unread(user_id)

    def detail(self, notification_id: str) -> dict[str, Any] | None:
        return self.repository.get(notification_id)

    def bell(self, user_id: str) -> dict[str, Any]:
        latest = self.repository.list_by_user(user_id=user_id, limit=5, unread_only=True)
        unread = self.repository.count_unread(user_id)
        return {
            "user_id": user_id,
            "has_new": unread > 0,
            "unread": unread,
            "latest": latest,
        }
