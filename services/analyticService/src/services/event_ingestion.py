from typing import Any

try:
    from prometheus_client import Counter
except ModuleNotFoundError:
    class _NoopCounter:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def labels(self, *args: Any, **kwargs: Any) -> "_NoopCounter":
            return self

        def inc(self) -> None:
            pass

    Counter = _NoopCounter

from src.infra.database import EventLogRepository

EVENTS_INGESTED = Counter(
    "analytic_events_ingested_total",
    "Total de eventos ingeridos pelo analyticService.",
    ["source_service", "routing_key"],
)


class EventIngestionService:
    def __init__(self, repository: EventLogRepository) -> None:
        self.repository = repository

    async def ingest(self, payload: dict[str, Any], routing_key: str) -> None:
        saved = self.repository.save(payload, routing_key)
        EVENTS_INGESTED.labels(
            source_service=saved["source_service"],
            routing_key=saved["routing_key"],
        ).inc()

    def list_recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.repository.list_recent(limit=limit)

    def count_by_source(self) -> list[dict[str, Any]]:
        return self.repository.count_by_source()
