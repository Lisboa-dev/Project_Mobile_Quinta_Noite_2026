from src.infra.adapter.repository.base import SQLiteRepository


class RuleRepository(SQLiteRepository):
    async def save(self, rule) -> None:
        rule_id = self._entity_id(rule)
        data = self._load(self._dump(rule))
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
                    data.get("target"),
                    data.get("targetType"),
                    data.get("ruleEffect", "NULL"),
                    self._dump(rule),
                ),
            )
        await self._cache_entity("rules", rule_id, rule)

    async def delete(self, id: str) -> None:
        self._delete_by_id("rules", id)
        await self._invalidate_entity("rules", id)

    async def deleteRule(self, rule_id: str) -> bool:
        deleted = self._delete_by_id("rules", rule_id)
        await self._invalidate_entity("rules", rule_id)
        return deleted

    async def getDayRules(self) -> list:
        with self._db.connect() as connection:
            rows = connection.execute(
                "SELECT data FROM rules WHERE target_type IS NULL OR target_type = 'DAY'"
            ).fetchall()
            return [self._load(row["data"]) for row in rows]
