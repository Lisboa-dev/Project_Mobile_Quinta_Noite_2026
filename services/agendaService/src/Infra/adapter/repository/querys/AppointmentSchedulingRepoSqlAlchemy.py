from typing import Any

from src.infra.adapter.repository.base import SQLiteRepository
from src.infra.cache import RuleOptimizationCache
from src.infra.cache.OptimizeRules import OptimizeRules
from src.infra.mapper.DomainMapper import (
    AppointmentMapper,
    DayMapper,
    DoctorMapper,
    PatientMapper,
    RoomMapper,
    RuleMapper,
)
from src.modules.agenda.aplication.dtos.repositorys.output.AppointmentSchedulingOutputDTO import (
    AppointmentSchedulingOutputDTO,
)
from src.modules.agenda.domain.entities import Day
from src.modules.agenda.domain.rules import BaseRule, RuleEffect, TargetType
from src.modules.agenda.domain.valueObjects import AppointmentType, Date, DayStatus, Hour
from src.modules.agenda.domain.valueObjects.RangeTime import RangeTime


class AppointmentSchedulingRepository(SQLiteRepository):
    _rule_optimization_cache = RuleOptimizationCache()

    async def getContext(self, appointmentScheduling):
        availability_context = await self.getAvailabilityContext(appointmentScheduling)
        appointments = availability_context["appointments"]
        doctor_id = str(availability_context["doctor"].id)
        patient_id = str(availability_context["patient"].id)

        return AppointmentSchedulingOutputDTO(
            doctor=availability_context["doctor"],
            day=availability_context["day"],
            patient=availability_context["patient"],
            rooms=availability_context["rooms"],
            room=availability_context["rooms"],
            appointmentsToDoctor=[
                appointment
                for appointment in appointments
                if str(appointment.doctor_id) == doctor_id
            ],
            appointmentsToPatient=[
                appointment
                for appointment in appointments
                if str(appointment.patient_id) == patient_id
            ],
            type=AppointmentType(
                name=appointmentScheduling.type,
                duration=30,
                description=appointmentScheduling.type,
            ),
            time=Hour(appointmentScheduling.time),
            rangeTime=availability_context["rangeTime"],
            appointments=appointments,
        )

    async def getAvailabilityContext(self, appointmentScheduling) -> dict[str, Any]:
        appointment_date = self._parse_date(appointmentScheduling.date)
        weekday = int(appointmentScheduling.weekday)
        appointment_type = AppointmentType(
            name=appointmentScheduling.type,
            duration=30,
            description=appointmentScheduling.type,
        )
        requested_range = RangeTime.generate(appointmentScheduling.time, appointment_type.duration)

        patient = PatientMapper.toDomain(
            await self._fetch_json_cached("patients", str(appointmentScheduling.patient))
        )
        doctor = DoctorMapper.toDomain(
            await self._fetch_json_cached("doctors", str(appointmentScheduling.doctor))
        )
        day = DayMapper.toDomain(await self._fetch_json_cached("days", str(appointment_date)))

        if patient is None:
            raise ValueError("Patient not found")
        if doctor is None:
            raise ValueError("Doctor not found")

        rooms = await self._load_rooms(appointmentScheduling.room)
        appointments = await self._load_appointments(str(appointment_date))

        for room in rooms:
            room.appointment_list = [
                appointment
                for appointment in appointments
                if str(appointment.room_id) == str(room.id)
            ]

        rules_by_context = await self._build_rules_context(
            date=appointment_date,
            weekday=weekday,
            doctor_id=str(doctor.id),
            rooms=rooms,
        )

        day_rules = rules_by_context["rule_days"]
        doctor_rules = rules_by_context["rule_doctors"]
        rule_rooms = rules_by_context["rule_rooms"]

        day_block = self._first_block(day_rules, appointment_date, weekday)
        doctor_block = self._first_block(doctor_rules, appointment_date, weekday)

        if day is None:
            day = Day(
                rooms=[],
                date=appointment_date,
                weekday=weekday,
                availability=True,
                status=DayStatus.AVAILABLE,
                rules=[],
            )

        if day_block is not None:
            day.rules = [day_block]
            day.availability = False
            day.status = DayStatus.BLOCKED
            rooms = []
            rule_rooms = {}
        else:
            day.rules = day_rules

        if doctor_block is not None:
            doctor.rules = [doctor_block]
            doctor.availability = False
            rooms = []
            rule_rooms = {}
        else:
            doctor.rules = doctor_rules

        available_rooms = []
        for room in rooms:
            room_rules = rule_rooms.get(str(room.id), [])
            room_block = self._first_block(room_rules, appointment_date, weekday)
            if room_block is not None:
                continue

            room.rules = room_rules
            if room.verifyInDisponibility(requested_range):
                available_rooms.append(room)

        day.rooms = available_rooms

        return {
            "day": day,
            "rule_days": day.rules,
            "doctor": doctor,
            "rule_doctors": doctor.rules,
            "rooms": available_rooms,
            "rule_rooms": {
                str(room.id): room.rules
                for room in available_rooms
            },
            "patient": patient,
            "appointments": appointments,
            "rangeTime": requested_range,
        }

    async def _build_rules_context(
        self,
        date: Date,
        weekday: int,
        doctor_id: str,
        rooms: list,
    ) -> dict[str, Any]:
        await self._ensure_rules_loaded_in_memory()

        day_rules = self._rules_for_day(
            await self._get_rules_layer(f"day:{date}", TargetType.DAY, str(date)),
            date,
            weekday,
        )
        doctor_rules = self._rules_for_day(
            await self._get_rules_layer(f"doctor:{doctor_id}", TargetType.DOCTOR, doctor_id),
            date,
            weekday,
        )

        rule_rooms: dict[str, list[BaseRule]] = {}
        for room in rooms:
            room_id = str(room.id)
            room_rules = self._rules_for_day(
                await self._get_rules_layer(f"room:{room_id}", TargetType.ROOM, room_id),
                date,
                weekday,
            )
            block = self._first_block(room_rules, date, weekday)
            rule_rooms[room_id] = [block] if block is not None else room_rules

        day_block = self._first_block(day_rules, date, weekday)
        doctor_block = self._first_block(doctor_rules, date, weekday)

        return {
            "rule_days": [day_block] if day_block is not None else day_rules,
            "rule_doctors": [doctor_block] if doctor_block is not None else doctor_rules,
            "rule_rooms": rule_rooms,
        }

    async def _ensure_rules_loaded_in_memory(self) -> None:
        day_rules = await self._rule_optimization_cache._get_layer("day")
        doctor_rules = await self._rule_optimization_cache._get_layer("doctor")
        room_rules = await self._rule_optimization_cache._get_layer("room")
        if day_rules is None or doctor_rules is None or room_rules is None:
            await self._rule_optimization_cache.refresh_all_layers()

    async def _get_rules_layer(
        self,
        layer: str,
        target_type: TargetType,
        target: str | None = None,
    ) -> list[BaseRule]:
        cached = await self._rule_optimization_cache._get_layer(layer)
        if cached is not None:
            return cached

        rules = await self._load_rules_from_database(target_type, target)
        optimized = OptimizeRules().removeRedundantRules(rules)
        await self._rule_optimization_cache._set_layer(layer, optimized)
        return optimized

    async def _load_rules_from_database(
        self,
        target_type: TargetType,
        target: str | None = None,
    ) -> list[BaseRule]:
        params: list[Any] = [target_type.value]
        where = """
            (target_type IS NULL AND target IS NULL)
            OR (target_type = ? AND target IS NULL)
        """

        if target is not None:
            where += """
                OR (target_type = ? AND target = ?)
                OR (target_type IS NULL AND target = ?)
            """
            params.extend([target_type.value, target, target])

        with self._db.connect() as connection:
            rows = connection.execute(
                f"SELECT data FROM rules WHERE {where}",
                tuple(params),
            ).fetchall()

        rules = []
        for row in rows:
            rule = RuleMapper.toDomain(self._load(row["data"]))
            if isinstance(rule, BaseRule):
                rules.append(rule)
        return rules

    def _rules_for_day(
        self,
        rules: list[BaseRule],
        date: Date,
        weekday: int,
    ) -> list[BaseRule]:
        return OptimizeRules().removeRedundantRules(
            [rule for rule in rules if self._rule_matches_day(rule, date, weekday)]
        )

    def _rule_matches_day(self, rule: BaseRule, date: Date, weekday: int) -> bool:
        if rule.targetType == TargetType.DAY and rule.target is not None:
            try:
                if not self._parse_date(str(rule.target)).compare(date):
                    return False
            except Exception:
                return False
        if rule.date is not None and not rule.date.compare(date):
            return False
        if rule.weekday is not None and int(rule.weekday) != int(weekday):
            return False
        return True

    def _first_block(
        self,
        rules: list[BaseRule],
        date: Date,
        weekday: int,
    ) -> BaseRule | None:
        for rule in rules:
            if rule.ruleEffect == RuleEffect.BLOCK and self._rule_matches_day(rule, date, weekday):
                return rule
        return None

    async def _load_rooms(self, room_id: str | None = None) -> list:
        if room_id:
            room = RoomMapper.toDomain(await self._fetch_json_cached("rooms", str(room_id)))
            return [room] if room is not None else []

        cache_key = self._list_cache_key("rooms", "appointment-scheduling")
        cached = await self._redis.get_json(cache_key)
        if isinstance(cached, list):
            return [room for room in (RoomMapper.toDomain(item) for item in cached) if room]

        with self._db.connect() as connection:
            rows = connection.execute("SELECT data FROM rooms ORDER BY created_at ASC").fetchall()

        result = [self._load(row["data"]) for row in rows]
        await self._redis.set_json(cache_key, result)
        return [room for room in (RoomMapper.toDomain(item) for item in result) if room]

    async def _load_appointments(self, day_id: str) -> list:
        with self._db.connect() as connection:
            rows = connection.execute(
                "SELECT data FROM appointments WHERE date_id = ?",
                (day_id,),
            ).fetchall()
        return [
            appointment
            for appointment in (AppointmentMapper.toDomain(self._load(row["data"])) for row in rows)
            if appointment is not None
        ]

    def _parse_date(self, value: str) -> Date:
        clean = value.split("T", 1)[0]
        if "/" in clean:
            day, month, year = clean.split("/")
            return Date(day=int(day), month=int(month), year=int(year))
        year, month, day = clean.split("-")
        return Date(day=int(day), month=int(month), year=int(year))
