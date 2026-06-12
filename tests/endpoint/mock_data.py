"""Dados para testes de endpoint contra os services em execucao."""

from datetime import datetime, timedelta
from typing import Any
import random


ADMIN_ID = "550e8400-e29b-41d4-a716-446655440000"
CLINIC_ID = "550e8400-e29b-41d4-a716-446655440001"
DOCTOR_ID = "550e8400-e29b-41d4-a716-446655440002"
PATIENT_ID = "550e8400-e29b-41d4-a716-446655440003"
ROOM_ID = "550e8400-e29b-41d4-a716-446655440005"


def _suffix() -> int:
    return random.randint(1000, 9999)


def clinic_data() -> dict[str, Any]:
    return {
        "name": "Clinica Central",
        "rules": [],
        "triggered_by_id": ADMIN_ID,
    }


def room_data() -> dict[str, Any]:
    return {
        "name": "Consultorio 1",
        "triggered_by_id": ADMIN_ID,
    }


def doctor_data() -> dict[str, Any]:
    return {
        "id_extern": DOCTOR_ID,
        "name": "Dra Endpoint",
        "triggered_by_id": ADMIN_ID,
    }


def patient_data() -> dict[str, Any]:
    return {
        "id_extern": PATIENT_ID,
        "name": "Paciente Endpoint",
        "triggered_by_id": ADMIN_ID,
    }


def appointment_data() -> dict[str, Any]:
    tomorrow = datetime.now() + timedelta(days=1)
    return {
        "scheduler_id": ADMIN_ID,
        "date": tomorrow.date().isoformat(),
        "weekday": str(tomorrow.weekday()),
        "doctor": DOCTOR_ID,
        "patient": PATIENT_ID,
        "time": "09:00",
        "type": "consulta",
        "triggered_by_id": ADMIN_ID,
    }


def appointment_type_data() -> dict[str, Any]:
    return {
        "name": "Consulta Geral",
        "duration": 30,
        "description": "Consulta geral de atendimento",
        "triggered_by_id": ADMIN_ID,
    }


def calendar_data() -> dict[str, Any]:
    return {
        "mes": datetime.now().month,
        "ano": datetime.now().year,
        "triggered_by_id": ADMIN_ID,
    }


def calendar_day_data() -> dict[str, Any]:
    return {
        "data": {
            "availability": True,
            "status": "AVAILABLE",
        },
        "triggered_by_id": ADMIN_ID,
    }


def rule_data_block() -> dict[str, Any]:
    tomorrow = datetime.now() + timedelta(days=1)
    return {
        "date": tomorrow.date().isoformat(),
        "description": "Bloqueio de atendimento",
        "target": DOCTOR_ID,
        "targetType": "doctor",
        "nome": "Bloqueio doctor",
        "triggered_by_id": ADMIN_ID,
    }


def rule_data_generic() -> dict[str, Any]:
    return {
        "ruleEffect": "allow",
        "targetType": "doctor",
        "rangeTime": {"start": "08:00", "end": "17:00"},
        "description": "Horario disponivel",
        "nome": "Regra generica doctor",
        "triggered_by_id": ADMIN_ID,
    }


def rule_data_specific() -> dict[str, Any]:
    return {
        "ruleEffect": "deny",
        "id": DOCTOR_ID,
        "type": "doctor",
        "rangeTime": {"start": "12:00", "end": "13:00"},
        "description": "Intervalo de almoco",
        "nome": "Intervalo doctor",
        "triggered_by_id": ADMIN_ID,
    }


def rule_data_specific_day() -> dict[str, Any]:
    tomorrow = datetime.now() + timedelta(days=1)
    return {
        "ruleEffect": "allow",
        "rangeTime": {"start": "14:00", "end": "18:00"},
        "description": "Atendimento extra",
        "date": tomorrow.date().isoformat(),
        "target": ROOM_ID,
        "targetType": "room",
        "nome": "Extra sala",
        "triggered_by_id": ADMIN_ID,
    }


def rule_data_week() -> dict[str, Any]:
    return {
        "ruleEffect": "allow",
        "rangeTime": {"start": "08:00", "end": "12:00"},
        "description": "Atendimento semanal",
        "weekday": 1,
        "target": DOCTOR_ID,
        "targetType": "doctor",
        "nome": "Segunda doctor",
        "triggered_by_id": ADMIN_ID,
    }


def user_data() -> dict[str, Any]:
    suffix = _suffix()
    return {
        "userName": f"user_test_{suffix}",
        "email": f"user_test_{suffix}@clinica.local",
        "password": "TestPassword123!",
        "name": f"User Test {suffix}",
        "cargo": "PACIENTE",
    }


def admin_data() -> dict[str, Any]:
    suffix = _suffix()
    return {
        "userName": f"admin_test_{suffix}",
        "email": f"admin_test_{suffix}@clinica.local",
        "password": "AdminTest123!",
        "name": f"Admin Test {suffix}",
        "cargo": "ADMIN",
    }


def medic_data() -> dict[str, Any]:
    suffix = _suffix()
    return {
        "userName": f"medic_test_{suffix}",
        "email": f"medic_test_{suffix}@clinica.local",
        "password": "MedicTest123!",
        "name": f"Medic Test {suffix}",
        "crm": f"CRM-{suffix}",
    }


def pacient_data() -> dict[str, Any]:
    suffix = _suffix()
    return {
        "userName": f"pacient_test_{suffix}",
        "email": f"pacient_test_{suffix}@clinica.local",
        "password": "PacientTest123!",
        "name": f"Pacient Test {suffix}",
        "cpf": f"1234567{suffix:04d}",
    }


def atendent_data() -> dict[str, Any]:
    suffix = _suffix()
    return {
        "userName": f"atendent_test_{suffix}",
        "email": f"atendent_test_{suffix}@clinica.local",
        "password": "AtendentTest123!",
        "name": f"Atendent Test {suffix}",
        "cpf": f"7654321{suffix:04d}",
    }


def login_data() -> dict[str, Any]:
    return {
        "email": "admin@clinica.local",
        "password": "Admin123!",
    }


def invalid_login_data() -> dict[str, Any]:
    return {
        "email": "invalid@clinica.local",
        "password": "InvalidPassword123!",
    }


def event_data() -> dict[str, Any]:
    return {
        "source": "agenda-service",
        "event": "appointment.created",
        "payload": {
            "appointment_id": "550e8400-e29b-41d4-a716-446655440004",
            "timestamp": datetime.now().isoformat(),
        },
    }
