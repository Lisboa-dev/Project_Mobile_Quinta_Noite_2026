from collections import defaultdict
from typing import Any, Callable, Awaitable

from src.infra.clients.redis_client import RedisClient
from src.infra.config.settings import settings
from src.infra.database import Database, database
from src.infra.mapper.DomainMapper import RuleMapper
from src.infra.mapper.JsonMapper import to_primitive
from src.infra.cache.OptimizeRules import OptimizeRules
from src.modules.agenda.domain.rules import BaseRule, TargetType


class RuleOptimizationCache:
    _key_prefix = "agenda:rules:optimized"

    def __init__(self, db: Database = database, redis: RedisClient | None = None):
        self._db = db
        self._redis = redis or RedisClient()

    async def get_day_rules(self, loader: Callable[[], Awaitable[list[Any]]]) -> list[BaseRule]:
        return await self._get_or_build("day", loader)

    async def get_doctor_rules(self, loader: Callable[[], Awaitable[list[Any]]]) -> list[BaseRule]:
        return await self._get_or_build("doctor", loader)

    async def get_room_rules(self, loader: Callable[[], Awaitable[list[Any]]]) -> list[BaseRule]:
        return await self._get_or_build("room", loader)

    async def refresh_all_layers(self) -> dict[str, int]:
        rules = self._load_all_rules()
        base_rules = self._base_rules(rules)
        layers: dict[str, list[BaseRule]] = {
            "base": base_rules,
            "day": base_rules + self._context_rules(rules, TargetType.DAY),
            "doctor": base_rules + self._generic_rules(rules, TargetType.DOCTOR),
            "room": base_rules + self._generic_rules(rules, TargetType.ROOM),
        }

        for target_type, grouped_rules in self._target_rules(rules).items():
            generic_layer = layers.get(target_type.lower(), base_rules)
            for target, target_rules in grouped_rules.items():
                layers[f"{target_type.lower()}:{target}"] = generic_layer + target_rules

        await self.invalidate_all()
        for layer, layer_rules in layers.items():
            await self._set_layer(layer, self._optimize(layer_rules))
        return {layer: len(layer_rules) for layer, layer_rules in layers.items()}

    async def invalidate_all(self) -> None:
        await self._redis.delete_pattern(f"{self._key_prefix}:*")

    async def _get_or_build(self, layer: str, loader: Callable[[], Awaitable[list[Any]]]) -> list[BaseRule]:
        cached = await self._get_layer(layer)
        if cached is not None:
            return cached

        rules = self._to_domain_rules(await loader())
        optimized = self._optimize(rules)
        await self._set_layer(layer, optimized)
        return optimized

    async def _get_layer(self, layer: str) -> list[BaseRule] | None:
        cached = await self._redis.get_json(self._key(layer))
        if cached is None:
            return None
        return self._to_domain_rules(cached)

    async def _set_layer(self, layer: str, rules: list[BaseRule]) -> None:
        await self._redis.set_json(
            self._key(layer),
            to_primitive(rules),
            ttl=settings.redis_cache_ttl_seconds,
        )

    def _load_all_rules(self) -> list[BaseRule]:
        with self._db.connect() as connection:
            rows = connection.execute("SELECT data FROM rules").fetchall()
        return self._to_domain_rules([row["data"] for row in rows])

    def _to_domain_rules(self, values: list[Any] | None) -> list[BaseRule]:
        rules: list[BaseRule] = []
        for value in values or []:
            rule = RuleMapper.toDomain(value)
            if isinstance(rule, BaseRule):
                rules.append(rule)
        return rules

    def _optimize(self, rules: list[BaseRule]) -> list[BaseRule]:
        return OptimizeRules().removeRedundantRules(rules)

    def _base_rules(self, rules: list[BaseRule]) -> list[BaseRule]:
        return [rule for rule in rules if rule.targetType is None and rule.target is None]

    def _generic_rules(self, rules: list[BaseRule], target_type: TargetType) -> list[BaseRule]:
        return [rule for rule in rules if rule.targetType == target_type and rule.target is None]

    def _context_rules(self, rules: list[BaseRule], target_type: TargetType) -> list[BaseRule]:
        return [rule for rule in rules if rule.targetType == target_type]

    def _target_rules(self, rules: list[BaseRule]) -> dict[str, dict[str, list[BaseRule]]]:
        grouped_rules: dict[str, dict[str, list[BaseRule]]] = defaultdict(lambda: defaultdict(list))
        for rule in rules:
            if rule.targetType is None or rule.target is None:
                continue
            grouped_rules[rule.targetType.value][str(rule.target)].append(rule)
        return grouped_rules

    def _key(self, layer: str) -> str:
        return f"{self._key_prefix}:{layer}"
