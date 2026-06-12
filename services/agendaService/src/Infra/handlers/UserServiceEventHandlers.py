from dataclasses import dataclass
from typing import Any
from unicodedata import normalize

from src.modules.agenda.aplication.dtos.useCase.command.DoctorUseCasesDTO import CreateDoctorCommand
from src.modules.agenda.aplication.dtos.useCase.command.PatientUseCasesDTO import CreatePatientCommand
from src.modules.agenda.aplication.useCases.commands.doctor.CreateDoctor import CreateDoctorUseCase
from src.modules.agenda.aplication.useCases.commands.doctor.DeleteDoctor import DeleteDoctorUseCase
from src.modules.agenda.aplication.useCases.commands.patient.CreatePacient import CreatePatientUseCase
from src.modules.agenda.aplication.useCases.commands.patient.DeletePacient import DeletePatientUseCase


DOCTOR_CARGOS = {"doctor", "medic", "medico"}
PATIENT_CARGOS = {"patient", "pacient", "paciente"}


def _payload_value(payload: Any, *names: str, default: Any = None) -> Any:
    event_payload = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), dict) else payload
    for name in names:
        if isinstance(event_payload, dict) and name in event_payload:
            return event_payload[name]
        if hasattr(event_payload, name):
            return getattr(event_payload, name)
        if isinstance(payload, dict) and name in payload:
            return payload[name]
        if hasattr(payload, name):
            return getattr(payload, name)
    return default


def _cargo_is(cargo: Any, expected: set[str]) -> bool:
    if cargo is None:
        return True
    normalized = normalize("NFKD", str(cargo).strip().lower())
    ascii_cargo = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_cargo in expected


def _string_id(value: Any) -> str:
    if value is None:
        raise ValueError("event payload must contain an external user id")
    return str(value)


def _name(value: Any) -> str:
    if value is None or str(value).strip() == "":
        raise ValueError("event payload must contain userName/name")
    return str(value)


def _handled_output(output: Any) -> tuple[bool, str | None]:
    success = getattr(output, "success", bool(output))
    message = getattr(output, "message", None)
    return bool(success), message


@dataclass(frozen=True)
class UserServiceEventResult:
    handled: bool
    entity: str
    external_id: str | None = None
    reason: str | None = None


class UserServiceDoctorCreatedHandler:
    def __init__(self, use_case: CreateDoctorUseCase):
        self._use_case = use_case

    async def handle(self, payload: Any) -> UserServiceEventResult:
        cargo = _payload_value(payload, "cargo", "role")
        if not _cargo_is(cargo, DOCTOR_CARGOS):
            return UserServiceEventResult(False, "doctor", reason=f"ignored cargo={cargo}")

        external_id = _string_id(_payload_value(payload, "user_id", "id", "medic_id", "doctor_id"))
        name = _name(_payload_value(payload, "userName", "username", "name", "nome"))
        triggered_by_id = _payload_value(payload, "triggered_by_id", "triggeredById")
        output = await self._use_case.execute(
            CreateDoctorCommand(id_extern=external_id, name=name, triggered_by_id=triggered_by_id)
        )
        handled, reason = _handled_output(output)
        return UserServiceEventResult(handled, "doctor", external_id=external_id, reason=reason)


class UserServicePatientCreatedHandler:
    def __init__(self, use_case: CreatePatientUseCase):
        self._use_case = use_case

    async def handle(self, payload: Any) -> UserServiceEventResult:
        cargo = _payload_value(payload, "cargo", "role")
        if not _cargo_is(cargo, PATIENT_CARGOS):
            return UserServiceEventResult(False, "patient", reason=f"ignored cargo={cargo}")

        external_id = _string_id(_payload_value(payload, "pacient_id", "patient_id", "user_id", "id"))
        name = _name(_payload_value(payload, "userName", "username", "name", "nome"))
        triggered_by_id = _payload_value(payload, "triggered_by_id", "triggeredById")
        output = await self._use_case.execute(
            CreatePatientCommand(id=external_id, name=name, triggered_by_id=triggered_by_id)
        )
        handled, reason = _handled_output(output)
        return UserServiceEventResult(handled, "patient", external_id=external_id, reason=reason)


class UserServiceDoctorDeletedHandler:
    def __init__(self, use_case: DeleteDoctorUseCase):
        self._use_case = use_case

    async def handle(self, payload: Any) -> UserServiceEventResult:
        cargo = _payload_value(payload, "cargo", "role")
        if not _cargo_is(cargo, DOCTOR_CARGOS):
            return UserServiceEventResult(False, "doctor", reason=f"ignored cargo={cargo}")

        external_id = _string_id(_payload_value(payload, "user_id", "id", "medic_id", "doctor_id"))
        triggered_by_id = _payload_value(payload, "triggered_by_id", "triggeredById")
        output = await self._use_case.execute(external_id, triggered_by_id=triggered_by_id)
        handled, reason = _handled_output(output)
        return UserServiceEventResult(handled, "doctor", external_id=external_id, reason=reason)


class UserServicePatientDeletedHandler:
    def __init__(self, use_case: DeletePatientUseCase):
        self._use_case = use_case

    async def handle(self, payload: Any) -> UserServiceEventResult:
        cargo = _payload_value(payload, "cargo", "role")
        if not _cargo_is(cargo, PATIENT_CARGOS):
            return UserServiceEventResult(False, "patient", reason=f"ignored cargo={cargo}")

        external_id = _string_id(_payload_value(payload, "pacient_id", "patient_id", "user_id", "id"))
        triggered_by_id = _payload_value(payload, "triggered_by_id", "triggeredById")
        output = await self._use_case.execute(external_id, triggered_by_id=triggered_by_id)
        handled, reason = _handled_output(output)
        return UserServiceEventResult(handled, "patient", external_id=external_id, reason=reason)
