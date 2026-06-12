from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.services import EventIngestionService


class FakeEventLogRepository:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def save(self, payload: dict[str, Any], routing_key: str) -> dict[str, Any]:
        event_name = str(payload.get("event") or payload.get("type") or routing_key)
        item = {
            "id": len(self.items) + 1,
            "source_service": self._source_from_route(routing_key),
            "event_name": event_name,
            "routing_key": routing_key,
            "payload": payload,
            "created_at": datetime.now(timezone.utc),
        }
        self.items.append(item)
        return item

    def list_recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return list(reversed(self.items))[:limit]

    def count_by_source(self) -> list[dict[str, Any]]:
        totals: dict[str, int] = {}
        for item in self.items:
            source = item["source_service"]
            totals[source] = totals.get(source, 0) + 1
        return [
            {"source_service": source, "total": total}
            for source, total in sorted(totals.items())
        ]

    def _source_from_route(self, routing_key: str) -> str:
        if routing_key.startswith("users."):
            return "users-service"
        if routing_key.startswith("agenda."):
            return "agenda-service"
        return "unknown"


class AnalyticTestProvider:
    def event_repository(self) -> FakeEventLogRepository:
        return FakeEventLogRepository()

    def event_ingestion_service(
        self,
        repository: FakeEventLogRepository | None = None,
    ) -> EventIngestionService:
        return EventIngestionService(repository or self.event_repository())
