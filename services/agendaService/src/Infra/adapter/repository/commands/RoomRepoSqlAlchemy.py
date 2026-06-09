from src.infra.adapter.repository.base import SQLiteRepository
from src.infra.cache import RuleOptimizationCache
from src.infra.mapper.DomainMapper import RoomMapper
from src.infra.mapper.DomainMapper import RuleMapper


class RoomRepository(SQLiteRepository):
    _rule_optimization_cache = RuleOptimizationCache()

    async def save(self, room) -> None:
        room_id = self._entity_id(room)
        with self._db.connect() as connection:
            connection.execute(
                """
                INSERT INTO rooms (id, name, data, updated_at)
                VALUES (?, ?, ?::jsonb, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    data = excluded.data,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (room_id, room.name, self._dump(room)),
            )
        await self._cache_entity("rooms", room_id, room)

    async def update(self, room) -> bool:
        await self.save(room)
        return True

    async def delete(self, room_id: str) -> None:
        self._delete_by_id("rooms", room_id)
        await self._invalidate_entity("rooms", room_id)

    async def deleteRoom(self, room_id: str) -> None:
        await self.delete(room_id)

    async def getRoom(self, room_id: str):
        return RoomMapper.toDomain(await self._fetch_json_cached("rooms", room_id))

    async def getGenericRulesRoom(self) -> list:
        return await self._rule_optimization_cache.get_room_rules(self._load_room_generic_rules)

    async def _load_room_generic_rules(self) -> list:
        with self._db.connect() as connection:
            rows = connection.execute(
                """
                SELECT data FROM rules
                WHERE (target_type IS NULL AND target IS NULL)
                   OR (target_type = 'ROOM' AND target IS NULL)
                """
            ).fetchall()
            return [RuleMapper.toDomain(self._load(row["data"])) for row in rows]
