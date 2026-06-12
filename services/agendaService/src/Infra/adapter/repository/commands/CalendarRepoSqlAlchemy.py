from src.infra.adapter.repository.base import SQLiteRepository
from src.infra.mapper.DomainMapper import DayMapper
from src.modules.agenda.domain.entities import Day


class CalendarRepository(SQLiteRepository):
    async def save(self, calendar) -> None:
        day = calendar
        date = day.date
        day_id = str(day.id)
        with self._db.connect() as connection:
            connection.execute(
                """
                INSERT INTO days (id, year, month, day, weekday, data, updated_at)
                VALUES (?, ?, ?, ?, ?, ?::jsonb, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    year = excluded.year,
                    month = excluded.month,
                    day = excluded.day,
                    weekday = excluded.weekday,
                    data = excluded.data,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    day_id,
                    int(date.year),
                    int(date.month),
                    int(date.day),
                    int(day.weekday),
                    self._dump(day),
                ),
            )
        await self._cache_entity("days", day_id, day)

    async def saveMany(self, moths: list[list[Day]]) -> None:
        if not moths:
            return

        with self._db.connect() as connection:
            for days in moths :
              for day in days:
                date = day.date
                connection.execute(
                    """
                    INSERT INTO days (id, year, month, day, weekday, data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?::jsonb, CURRENT_TIMESTAMP)
                    ON CONFLICT(id) DO UPDATE SET
                        year = excluded.year,
                        month = excluded.month,
                        day = excluded.day,
                        weekday = excluded.weekday,
                        data = excluded.data,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        str(day.id),
                        int(date.year),
                        int(date.month),
                        int(date.day),
                        int(day.weekday),
                        self._dump(day),
                    ),
                )

        await self._warm_calendar_cache(days)

    async def update(self, calendar) -> None:
        await self.save(calendar)

    async def updateDay(self, day: Day) -> None:
        await self.save(day)

    async def get(self, day_id: str):
        return DayMapper.toDomain(await self._fetch_json_cached("days", day_id))

    async def delete(self, ano: str | int | None = None) -> None:
        with self._db.connect() as connection:
            if ano is None:
                connection.execute("DELETE FROM days")
            else:
                connection.execute("DELETE FROM days WHERE year = ?", (int(ano),))
        await self._redis.delete_pattern(self._list_cache_key("days", "*"))

    async def _warm_calendar_cache(self, days: list[Day]) -> None:
        grouped_by_year: dict[int, list[Day]] = {}
        grouped_by_month: dict[tuple[int, int], list[Day]] = {}

        for day in days:
            date = day.date
            year = int(date.year)
            month = int(date.month)
            grouped_by_year.setdefault(year, []).append(day)
            grouped_by_month.setdefault((year, month), []).append(day)
            await self._redis.set_json(
                self._cache_key("days", str(day.id)),
                self._load(self._dump(day)),
            )

        await self._redis.delete_pattern(self._list_cache_key("days", "*"))

        for year, year_days in grouped_by_year.items():
            await self._redis.set_json(
                self._list_cache_key("days", f"year:{year}:month:None:limit:None:offset:0"),
                [self._load(self._dump(day)) for day in self._ordered_days(year_days)],
            )

        for (year, month), month_days in grouped_by_month.items():
            await self._redis.set_json(
                self._list_cache_key("days", f"year:{year}:month:{month}:limit:None:offset:0"),
                [self._load(self._dump(day)) for day in self._ordered_days(month_days)],
            )

    def _ordered_days(self, days: list[Day]) -> list[Day]:
        return sorted(days, key=lambda day: (int(day.date.year), int(day.date.month), int(day.date.day)))
