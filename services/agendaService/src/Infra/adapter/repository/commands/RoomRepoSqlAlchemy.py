from src.infra.adapter.repository.base import SQLiteRepository


class RoomRepository(SQLiteRepository):
    async def save(self, room) -> None:
        room_id = self._entity_id(room)
        data = self._load(self._dump(room))
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
                (room_id, data.get("name", ""), self._dump(room)),
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
        return await self._fetch_json_cached("rooms", room_id)

    async def getGenericRulesRoom(self) -> list:
        with self._db.connect() as connection:
            rows = connection.execute(
                "SELECT data FROM rules WHERE target_type = 'ROOM' AND target IS NULL"
            ).fetchall()
            return [self._load(row["data"]) for row in rows]
