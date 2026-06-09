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
