from typing import Any, Optional, List, Dict

from src.infra.adapter.repository.base import SQLiteRepository
from src.modules.agenda.aplication.dtos.useCase.query import ListDaysQuery, ListQuery


class BaseQueryRepository(SQLiteRepository):
    table_name: str

    async def get_by_id(self, entity_id: str) -> dict | None:
        return await self._fetch_json_cached(self.table_name, entity_id)

    async def _list(self, query: ListQuery) -> list[dict]:
        cache_key = self._list_cache_key(self.table_name, f"limit:{query.limit}:offset:{query.offset}")
        cached = await self._redis.get_json(cache_key)
        if isinstance(cached, list):
            return cached
        sql = f"SELECT data FROM {self.table_name} ORDER BY created_at DESC"
        params: list[Any] = []
        if query.limit is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([query.limit, query.offset])
        with self._db.connect() as connection:
            rows = connection.execute(sql, tuple(params)).fetchall()
            result = [self._load(row["data"]) for row in rows]
            await self._redis.set_json(cache_key, result)
            return result


class AppointmentQueryRepository(BaseQueryRepository):
    table_name = "appointments"

    async def list_by_patient(self, patient_id: str, query: ListQuery) -> list[dict]:
        return await self._list_by_column("patient_id", patient_id, "patient", query)

    async def list_by_doctor(self, doctor_id: str, query: ListQuery) -> list[dict]:
        return await self._list_by_column("doctor_id", doctor_id, "doctor", query)

    async def _list_by_column(
        self,
        column_name: str,
        entity_id: str,
        cache_prefix: str,
        query: ListQuery,
    ) -> list[dict]:
        cache_key = self._list_cache_key(
            self.table_name,
            f"{cache_prefix}:{entity_id}:limit:{query.limit}:offset:{query.offset}",
        )
        cached = await self._redis.get_json(cache_key)
        if isinstance(cached, list):
            return cached

        sql = f"SELECT data FROM {self.table_name} WHERE {column_name} = ? ORDER BY created_at DESC"
        params: list[Any] = [entity_id]
        if query.limit is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([query.limit, query.offset])

        with self._db.connect() as connection:
            rows = connection.execute(sql, tuple(params)).fetchall()
            result = [self._load(row["data"]) for row in rows]
            await self._redis.set_json(cache_key, result)
            return result


class ClinicQueryRepository(BaseQueryRepository):
    table_name = "clinics"


class DoctorQueryRepository(BaseQueryRepository):
    table_name = "doctors"


class PatientQueryRepository(BaseQueryRepository):
    table_name = "patients"


class RoomQueryRepository(BaseQueryRepository):
    table_name = "rooms"

    async def get_admin_detail(self, room_id: str) -> dict | None:
        cache_key = self._room_admin_detail_cache_key(room_id)
        cached = await self._redis.get_json(cache_key)
        if isinstance(cached, dict):
            return cached

        room = await self.get_by_id(room_id)
        if room is None:
            return None

        appointments = await self._appointments_by_room_ids([room_id])
        rules = await self._rules_by_room_ids([room_id])
        result = self._room_admin_payload(
            room,
            appointments.get(room_id, []),
            rules.get(room_id, []),
        )
        await self._redis.set_json(cache_key, result)
        return result

    async def list_admin_detailed(self, query: ListQuery) -> list[dict]:
        cache_key = self._list_cache_key(
            self.table_name,
            f"admin:limit:{query.limit}:offset:{query.offset}",
        )
        cached = await self._redis.get_json(cache_key)
        if isinstance(cached, list):
            return cached

        rooms = await self._list(query)
        room_ids = [room_id for room_id in (self._json_id(room.get("id")) for room in rooms) if room_id]
        appointments_by_room = await self._appointments_by_room_ids(room_ids)
        rules_by_room = await self._rules_by_room_ids(room_ids)
        result = [
            self._room_admin_payload(
                room,
                appointments_by_room.get(self._json_id(room.get("id")) or "", []),
                rules_by_room.get(self._json_id(room.get("id")) or "", []),
            )
            for room in rooms
        ]
        await self._redis.set_json(cache_key, result)
        return result

    async def _appointments_by_room_ids(self, room_ids: list[str]) -> dict[str, list[dict]]:
        if not room_ids:
            return {}

        placeholders = ", ".join(["?"] * len(room_ids))
        with self._db.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT room_id, data
                FROM appointments
                WHERE room_id IN ({placeholders})
                ORDER BY created_at DESC
                """,
                tuple(room_ids),
            ).fetchall()

        grouped: dict[str, list[dict]] = {room_id: [] for room_id in room_ids}
        for row in rows:
            grouped.setdefault(str(row["room_id"]), []).append(self._load(row["data"]))
        return grouped

    async def _rules_by_room_ids(self, room_ids: list[str]) -> dict[str, list[dict]]:
        if not room_ids:
            return {}

        placeholders = ", ".join(["?"] * len(room_ids))
        with self._db.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT target, data
                FROM rules
                WHERE target_type = 'ROOM'
                  AND (target IS NULL OR target IN ({placeholders}))
                ORDER BY created_at DESC
                """,
                tuple(room_ids),
            ).fetchall()

        generic_rules = [self._load(row["data"]) for row in rows if row["target"] is None]
        grouped: dict[str, list[dict]] = {room_id: list(generic_rules) for room_id in room_ids}
        for row in rows:
            target = row["target"]
            if target is not None:
                grouped.setdefault(str(target), list(generic_rules)).append(self._load(row["data"]))
        return grouped

    def _room_admin_payload(self, room: dict, appointments: list[dict], rules: list[dict]) -> dict:
        return {
            **room,
            "rules": rules or list(room.get("rules") or []),
            "appointments": appointments,
            "appointments_count": len(appointments),
        }

    def _room_admin_detail_cache_key(self, room_id: str) -> str:
        return f"agenda:{self.table_name}:id:{room_id}:admin-detail"

    def _json_id(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, dict):
            nested_id = value.get("id")
            return str(nested_id) if nested_id is not None else None
        return str(value)


class AppointmentTypeQueryRepository(BaseQueryRepository):
    table_name = "appointment_types"


class RuleQueryRepository(BaseQueryRepository):
    table_name = "rules"

    async def get_by_id(self, entity_id: str) -> dict | None:
        return await self.detail(entity_id)

    async def detail(self, rule_id: str) -> dict | None:
        data = await self._fetch_json_cached(self.table_name, rule_id)
        return self._normalize_rule_payload(data) if data is not None else None

    async def _list(self, query: ListQuery) -> list[dict]:
        return await self.list_rules(query)

    async def list_rules(self, query: ListQuery) -> list[dict]:
        rule_type = self._normalize_rule_type(getattr(query, "type", None))
        target_id = getattr(query, "target_id", None) or getattr(query, "id", None)
        effect = self._normalize_effect(getattr(query, "ruleEffect", None))

        cache_key = self._list_cache_key(
            self.table_name,
            (
                f"rules:type:{rule_type}:target:{target_id}:effect:{effect}:"
                f"limit:{query.limit}:offset:{query.offset}"
            ),
        )
        cached = await self._redis.get_json(cache_key)
        if isinstance(cached, list):
            return cached

        sql = "SELECT data FROM rules"
        filters: list[str] = []
        params: list[Any] = []

        if rule_type is not None:
            filters.append("target_type = ?")
            params.append(rule_type)
        if target_id is not None:
            filters.append("target = ?")
            params.append(str(target_id))
        if effect is not None:
            filters.append("rule_effect = ?")
            params.append(effect)
        if filters:
            sql += " WHERE " + " AND ".join(filters)

        sql += " ORDER BY created_at DESC"
        if query.limit is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([query.limit, query.offset])

        with self._db.connect() as connection:
            rows = connection.execute(sql, tuple(params)).fetchall()

        result = [
            normalized
            for normalized in (self._normalize_rule_payload(self._load(row["data"])) for row in rows)
            if normalized is not None
        ]
        await self._redis.set_json(cache_key, result)
        return result

    async def admin_context(self) -> dict:
        cache_key = self._list_cache_key(self.table_name, "admin-context")
        cached = await self._redis.get_json(cache_key)
        if isinstance(cached, dict):
            return cached

        with self._db.connect() as connection:
            rows = connection.execute("SELECT data FROM rules ORDER BY created_at DESC").fetchall()

        rules = [
            normalized
            for normalized in (self._normalize_rule_payload(self._load(row["data"])) for row in rows)
            if normalized is not None
        ]
        context = {
            "generic": {
                "day": [],
                "doctor": [],
                "room": [],
            },
            "specific": {
                "days": [],
                "doctors": [],
                "rooms": [],
            },
            "week": {
                "days": [],
                "doctors": [],
                "rooms": [],
            },
            "blocks": {
                "days": [],
                "doctors": [],
                "rooms": [],
            },
            "all": rules,
        }

        for rule in rules:
            target_type = str(rule.get("type") or rule.get("targetType") or rule.get("target_type") or "").upper()
            target = rule.get("targetId") or rule.get("target")
            date = rule.get("date")
            weekday = rule.get("weekday")
            effect = str(rule.get("ruleEffect") or rule.get("rule_effect") or "").upper()

            if effect == "BLOCK":
                self._append_admin_rule(context["blocks"], target_type, target, date, rule)
            elif weekday is not None:
                self._append_admin_rule(context["week"], target_type, target, date, rule)
            elif target is None and date is None and target_type in {"DAY", "DOCTOR", "ROOM"}:
                context["generic"][target_type.lower()].append(rule)
            elif date is not None:
                context["specific"]["days"].append(rule)
            elif target is not None:
                self._append_admin_rule(context["specific"], target_type, target, date, rule)

        await self._redis.set_json(cache_key, context)
        return context

    def _append_admin_rule(
        self,
        bucket: dict[str, list[dict]],
        target_type: str,
        target: Any,
        date: Any,
        rule: dict,
    ) -> None:
        if date is not None or target_type == "DAY":
            bucket["days"].append(rule)
        elif target_type == "DOCTOR":
            bucket["doctors"].append(rule)
        elif target_type == "ROOM" or target is not None:
            bucket["rooms"].append(rule)

    def _normalize_rule_payload(self, rule: dict | None) -> dict | None:
        if rule is None:
            return None
        target_id = rule.get("targetId") or rule.get("target_id") or rule.get("target")
        rule_type = self._normalize_rule_type(rule.get("type") or rule.get("targetType") or rule.get("target_type"))
        normalized = dict(rule)
        normalized["targetId"] = str(target_id) if target_id is not None else None
        normalized["target"] = normalized["targetId"]
        normalized["type"] = rule_type
        normalized["targetType"] = rule_type
        return normalized

    def _normalize_rule_type(self, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if "." in text:
            text = text.rsplit(".", 1)[-1]
        text = text.upper()
        aliases = {
            "DAYS": "DAY",
            "DATE": "DAY",
            "DATES": "DAY",
            "DOCTORS": "DOCTOR",
            "MEDIC": "DOCTOR",
            "MEDICO": "DOCTOR",
            "ROOMS": "ROOM",
        }
        text = aliases.get(text, text)
        return text if text in {"DAY", "DOCTOR", "ROOM"} else None

    def _normalize_effect(self, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if "." in text:
            text = text.rsplit(".", 1)[-1]
        text = text.upper()
        aliases = {
            "ALLOW": "ADD",
            "AVAILABLE": "ADD",
            "DENY": "REMOVE",
            "DISALLOW": "REMOVE",
            "UNAVAILABLE": "REMOVE",
        }
        return aliases.get(text, text)


class CalendarQueryRepository(SQLiteRepository):
    async def get_by_id(self, day_id: str) -> dict | None:
        return await self._fetch_json_cached("days", day_id)

    async def list_month_for_front(self, year: int, month: int) -> list[dict]:
        days = await self._list(ListDaysQuery(year=year, month=month, limit=None, offset=0))
        return [self._front_day_payload(day) for day in days]

    async def _list(self, query: ListDaysQuery) -> list[dict]:
        full_cache_key = self._list_cache_key(
            "days",
            f"year:{query.year}:month:{query.month}:limit:None:offset:0",
        )
        cache_key = self._list_cache_key(
            "days",
            f"year:{query.year}:month:{query.month}:limit:{query.limit}:offset:{query.offset}",
        )
        cached = await self._redis.get_json(cache_key)
        if isinstance(cached, list):
            return cached

        full_cached = await self._redis.get_json(full_cache_key)
        if isinstance(full_cached, list):
            result = self._slice_days(full_cached, query.limit, query.offset)
            await self._redis.set_json(cache_key, result)
            return result

        sql = "SELECT data FROM days"
        params: list[Any] = []
        filters: list[str] = []

        if query.year is not None:
            filters.append("year = ?")
            params.append(query.year)
        if query.month is not None:
            filters.append("month = ?")
            params.append(query.month)

        if filters:
            sql += " WHERE " + " AND ".join(filters)

        sql += " ORDER BY year DESC, month DESC, day DESC"

        if query.limit is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([query.limit, query.offset])

        with self._db.connect() as connection:
            rows = connection.execute(sql, tuple(params)).fetchall()
            result = [self._load(row["data"]) for row in rows]
            await self._redis.set_json(cache_key, result)
            if query.limit is None and query.offset == 0:
                await self._redis.set_json(full_cache_key, result)
            return result

    def _slice_days(self, days: List[Dict], limit: Optional[int], offset: int) -> List[Dict]:
        if limit is None:
            return days[offset:]
        return days[offset : offset + limit]

    def _front_day_payload(self, day: dict) -> dict:
        is_available = bool(day.get("availability", False))
        status = str(day.get("status", "")).upper()
        if isinstance(day.get("status"), dict):
            status = str(day["status"].get("value", "")).upper()
        unavailable_statuses = {"BLOCKED", "HOLIDAY", "SCHEDULED"}
        availability_state = (
            "available"
            if is_available and status not in unavailable_statuses
            else "unavailable"
        )
        return {
            **day,
            "availabilityState": availability_state,
        }
        
