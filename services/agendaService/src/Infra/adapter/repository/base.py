import json
from typing import Any

from src.infra.database import Database, database
from src.infra.clients import RedisClient
from src.infra.mapper.JsonMapper import to_primitive
from src.infra.migrations import MigrationRunner


class SQLiteRepository:
    _migrated = False
    _redis = RedisClient()

    def __init__(self, db: Database = database):
        
        self._db = db
        self._ensure_migrated()

    def _ensure_migrated(self) -> None:
        if not SQLiteRepository._migrated:
            MigrationRunner(self._db).run()
            SQLiteRepository._migrated = True

    def _dump(self, value: Any) -> str:
        return json.dumps(to_primitive(value), ensure_ascii=False)

    def _load(self, value: str | None) -> dict:
        if not value:
            return {}
        if isinstance(value, dict):
            return value
        return json.loads(value)

    def _entity_id(self, entity) -> str:
        entity_id = getattr(entity, "id", None) or getattr(entity, "_id", None)
        return str(entity_id)

    def _fetch_json(self, table: str, entity_id: str) -> dict | None:
        with self._db.connect() as connection:
            row = connection.execute(
                f"SELECT data FROM {table} WHERE id = ?",
                (entity_id,),
            ).fetchone()
            return self._load(row["data"]) if row else None

    def _cache_key(self, table: str, entity_id: str) -> str:
        return f"agenda:{table}:id:{entity_id}"

    def _list_cache_key(self, table: str, suffix: str = "all") -> str:
        return f"agenda:{table}:list:{suffix}"

    async def _fetch_json_cached(self, table: str, entity_id: str) -> dict | None:
        key = self._cache_key(table, entity_id)
        cached = await self._redis.get_json(key)
        if isinstance(cached, dict):
            return cached
        value = self._fetch_json(table, entity_id)
        if value is not None:
            await self._redis.set_json(key, value)
        return value

    async def _cache_entity(self, table: str, entity_id: str, value: Any) -> None:
        data = self._load(self._dump(value)) if not isinstance(value, dict) else value
        await self._redis.set_json(self._cache_key(table, entity_id), data)
        await self._redis.delete_pattern(self._list_cache_key(table, "*"))

    async def _invalidate_entity(self, table: str, entity_id: str) -> None:
        await self._redis.delete(self._cache_key(table, entity_id))
        await self._redis.delete_pattern(self._list_cache_key(table, "*"))

    def _delete_by_id(self, table: str, entity_id: str) -> bool:
        with self._db.connect() as connection:
            cursor = connection.execute(
                f"DELETE FROM {table} WHERE id = ?",
                (entity_id,),
            )
            return cursor.rowcount > 0

    def log_event(self, event_name: str, routing_key: str, payload: dict) -> None:
        with self._db.connect() as connection:
            connection.execute(
                """
                INSERT INTO event_logs (service_name, event_name, routing_key, payload)
                VALUES (?, ?, ?, ?::jsonb)
                """,
                ("agenda-service", event_name, routing_key, self._dump(payload)),
            )
