from datetime import time
from typing import Any

from src.modules.agenda.domain.entities import Appointment, Clinic, Day, Doctor, Patient, Room
from src.modules.agenda.domain.rules import (
    BaseRule,
    BlockRule,
    GenericRule,
    RuleEffect,
    SpecificDayRule,
    SpecificRule,
    TargetType,
    WeekRule,
)
from src.modules.agenda.domain.valueObjects import AppointmentType, Date, DayStatus, Hour, RangeTime
from src.modules.agenda.domain.valueObjects.EnumAppointment import AppointmentStatus
from src.modules.agenda.domain.valueObjects.Id import ID


def _id(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return str(value.get("id")) if value.get("id") is not None else None
    return str(value)


def _time_text(value: Any) -> str:
    if isinstance(value, time):
        return value.strftime("%H:%M")
    text = str(value)
    return text[:5] if len(text) >= 5 else text


def _date(value: Any) -> Date:
    if isinstance(value, Date):
        return value
    if isinstance(value, dict):
        return Date(day=int(value["day"]), month=int(value["month"]), year=int(value["year"]))
    text = str(value)
    if "/" in text:
        day, month, year = text.split("/")
        return Date(day=int(day), month=int(month), year=int(year))
    year, month, day = text.split("-")
    return Date(day=int(day), month=int(month), year=int(year))


def _status(value: Any, enum_type, default):
    if isinstance(value, enum_type):
        return value
    if value is None:
        return default
    return enum_type[str(value).upper()]


def _range_time(value: Any, fallback_time: Any = None, duration: int = 30) -> RangeTime:
    if isinstance(value, RangeTime):
        return value
    if isinstance(value, dict):
        return RangeTime(_time_text(value["start_time"]), _time_text(value["end_time"]))
    if value:
        start, end = str(value).split("-", 1)
        return RangeTime(_time_text(start.strip()), _time_text(end.strip()))
    return RangeTime.generate(_time_text(fallback_time or "00:00"), duration)


def _appointment_type(value: Any) -> AppointmentType:
    if isinstance(value, AppointmentType):
        return value
    if isinstance(value, dict):
        return AppointmentType(
            name=str(value.get("name", "appointment")),
            duration=int(value.get("duration", 30)),
            description=str(value.get("description", "")),
        )
    return AppointmentType(name=str(value or "appointment"), duration=30, description=str(value or ""))


def _rules(value: Any) -> list[BaseRule]:
    rules: list[BaseRule] = []
    for item in value or []:
        rule = RuleMapper.toDomain(item)
        if rule is not None:
            rules.append(rule)
    return rules


class ClinicMapper:
    @staticmethod
    def toDomain(data: dict[str, Any] | Clinic | None) -> Clinic | None:
        if data is None or isinstance(data, Clinic):
            return data
        return Clinic(
            id=_id(data.get("id")),
            name=str(data.get("name", "")),
            rules=_rules(data.get("rules")),
        )

    @staticmethod
    def toPersistence(domain: Clinic):
        return domain


class DoctorMapper:
    @staticmethod
    def toDomain(data: dict[str, Any] | Doctor | None) -> Doctor | None:
        if data is None or isinstance(data, Doctor):
            return data
        return Doctor(
            id=_id(data.get("id")),
            externId=str(data.get("extern_id") or data.get("externId") or data.get("id") or ""),
            name=str(data.get("name", "")),
            rules=_rules(data.get("rules")),
            availability=bool(data.get("availability", True)),
        )

    @staticmethod
    def toPersistence(domain: Doctor):
        return domain


class PatientMapper:
    @staticmethod
    def toDomain(data: dict[str, Any] | Patient | None) -> Patient | None:
        if data is None or isinstance(data, Patient):
            return data
        return Patient(
            id=_id(data.get("id")),
            name=str(data.get("name", "")),
            externId=str(data.get("extern_id") or data.get("externId") or data.get("id") or ""),
            appointments=list(data.get("appointments") or data.get("appoiments") or []),
        )

    @staticmethod
    def toPersistence(domain: Patient):
        return domain


class RoomMapper:
    @staticmethod
    def toDomain(data: dict[str, Any] | Room | None) -> Room | None:
        if data is None or isinstance(data, Room):
            return data
        room = Room(
            id=_id(data.get("id")),
            name=str(data.get("name", "")),
            rules=_rules(data.get("rules")),
            disponibility=bool(data.get("disponibility", True)),
        )
        room.appointment_list = list(data.get("appointment_list") or data.get("appointmentList") or [])
        return room

    @staticmethod
    def toPersistence(domain: Room):
        return domain


class DayMapper:
    @staticmethod
    def toDomain(data: dict[str, Any] | Day | None) -> Day | None:
        if data is None or isinstance(data, Day):
            return data
        return Day(
            rooms=[room for room in (RoomMapper.toDomain(item) for item in data.get("rooms", [])) if room],
            date=_date(data["date"]),
            weekday=int(data.get("weekday", 0)),
            availability=bool(data.get("availability", True)),
            status=_status(data.get("status"), DayStatus, DayStatus.AVAILABLE),
            rules=_rules(data.get("rules")),
        )

    @staticmethod
    def toPersistence(domain: Day):
        return domain


class AppointmentMapper:
    @staticmethod
    def toDomain(data: dict[str, Any] | Appointment | None) -> Appointment | None:
        if data is None or isinstance(data, Appointment):
            return data
        appointment_type = _appointment_type(data.get("type") or data.get("appointment_type"))
        return Appointment(
            id=ID(_id(data.get("id"))),
            patient=str(data.get("patient_id") or data.get("patient") or ""),
            doctor=str(data.get("doctor_id") or data.get("doctor") or ""),
            room=str(data.get("room_id") or data.get("room") or ""),
            type=appointment_type,
            time=Hour(_time_text(data.get("time") or "00:00")),
            status=_status(data.get("status"), AppointmentStatus, AppointmentStatus.AVAILABLE),
            rangeTime=_range_time(data.get("rangeTime") or data.get("range_time"), data.get("time"), appointment_type.duration),
            date=str(data.get("date") or data.get("date_id") or ""),
        )

    @staticmethod
    def toPersistence(domain: Appointment):
        return domain


class CalendarMapper:
    @staticmethod
    def toDomain(data):
        return DayMapper.toDomain(data)

    @staticmethod
    def toPersistence(domain):
        return domain


class RuleMapper:
    @staticmethod
    def toDomain(data):
        if data is None or isinstance(data, BaseRule):
            return data
        if not isinstance(data, dict):
            return None

        rule_effect = _rule_effect(data.get("ruleEffect") or data.get("rule_effect"))
        target_type = _target_type(data.get("targetType") or data.get("target_type"))
        range_time = _optional_range_time(data.get("rangeTime") or data.get("range_time"))
        date = _optional_date(data.get("date"))
        weekday = data.get("weekday")
        target = data.get("target")
        description = data.get("description")
        nome = data.get("nome")

        if rule_effect == RuleEffect.BLOCK:
            rule = BlockRule(
                date=date,
                weekday=int(weekday) if weekday is not None else None,
                description=description,
                target=target,
                targetType=target_type,
                nome=nome,
            )
        elif date is not None:
            rule = SpecificDayRule(
                ruleEffect=rule_effect,
                rangeTime=range_time,
                description=str(description or ""),
                date=date,
                target=target,
                targetType=target_type,
                nome=nome,
            )
        elif weekday is not None:
            rule = WeekRule(
                ruleEffect=rule_effect,
                rangeTime=range_time,
                description=str(description or ""),
                weekday=int(weekday),
                target=target,
                targetType=target_type,
                nome=nome,
            )
        elif target is not None and target_type is None:
            rule = SpecificRule(
                ruleEffect=rule_effect,
                target=str(target),
                rangeTime=range_time,
                description=str(description or ""),
                nome=nome,
            )
        elif target_type is not None:
            rule = GenericRule(
                ruleEffect=rule_effect,
                targetType=target_type,
                rangeTime=range_time,
                description=str(description or ""),
                nome=nome,
            )
        else:
            rule = BaseRule(
                ruleEffect=rule_effect,
                rangeTime=range_time,
                description=description,
                target=target,
                targetType=target_type,
                nome=nome,
            )

        rule_id = _id(data.get("id"))
        if rule_id is not None:
            rule._id = rule_id
        return rule

    @staticmethod
    def toPersistence(domain):
        return domain


def _rule_effect(value: Any) -> RuleEffect:
    if isinstance(value, RuleEffect):
        return value
    if value is None:
        return RuleEffect.NULL
    return RuleEffect[str(value).upper()]


def _target_type(value: Any) -> TargetType | None:
    if isinstance(value, TargetType):
        return value
    if value is None:
        return None
    text = str(value).upper()
    if text in {"", "NULL", "NONE"}:
        return None
    return TargetType[text]


def _optional_range_time(value: Any) -> RangeTime | None:
    if value is None:
        return None
    return _range_time(value)


def _optional_date(value: Any) -> Date | None:
    if value is None:
        return None
    return _date(value)
