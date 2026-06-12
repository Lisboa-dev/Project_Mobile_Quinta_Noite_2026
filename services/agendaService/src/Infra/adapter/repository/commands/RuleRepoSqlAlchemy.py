from src.infra.adapter.repository.base import SQLiteRepository
from src.infra.cache import RuleOptimizationCache
from src.infra.mapper.DomainMapper import RuleMapper


class RuleRepository(SQLiteRepository):
    _rule_optimization_cache = RuleOptimizationCache()

    async def save(self, rule) -> None:
        rule_id = self._entity_id(rule)
        data = self._load(self._dump(rule))
        target = data.get("targetId") or data.get("target_id") or data.get("target")
        target_type = data.get("type") or data.get("targetType") or data.get("target_type")
        with self._db.connect() as connection:
            connection.execute(
                """
                INSERT INTO rules (id, target, target_type, rule_effect, data, updated_at)
                VALUES (?, ?, ?, ?, ?::jsonb, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    target = excluded.target,
                    target_type = excluded.target_type,
                    rule_effect = excluded.rule_effect,
                    data = excluded.data,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    rule_id,
                    target,
                    target_type,
                    data.get("ruleEffect", "NULL"),
                    self._dump(rule),
                ),
            )
        await self._cache_entity("rules", rule_id, rule)
        await self._rule_optimization_cache.invalidate_all()
        await self._invalidate_room_admin_cache()

    async def delete(self, id: str) -> None:
        self._delete_by_id("rules", id)
        await self._invalidate_entity("rules", id)
        await self._rule_optimization_cache.invalidate_all()
        await self._invalidate_room_admin_cache()

    async def deleteRule(self, rule_id: str) -> bool:
        deleted = self._delete_by_id("rules", rule_id)
        await self._invalidate_entity("rules", rule_id)
        await self._rule_optimization_cache.invalidate_all()
        await self._invalidate_room_admin_cache()
        return deleted

    async def getDayRules(self) -> list:
        return await self._rule_optimization_cache.get_day_rules(self._load_day_rules)

    async def _load_day_rules(self) -> list:
        with self._db.connect() as connection:
            rows = connection.execute(
                "SELECT data FROM rules WHERE target_type IS NULL OR target_type = 'DAY'"
            ).fetchall()
            return [RuleMapper.toDomain(self._load(row["data"])) for row in rows]

    async def _invalidate_room_admin_cache(self) -> None:
        await self._redis.delete_pattern(self._list_cache_key("rooms", "admin*"))
        await self._redis.delete_pattern("agenda:rooms:id:*:admin-detail")
