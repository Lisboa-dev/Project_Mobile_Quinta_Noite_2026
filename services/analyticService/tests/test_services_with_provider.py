import pytest


@pytest.mark.asyncio
async def test_event_ingestion_service_accepts_type_as_event_name(analytic_provider):
    repository = analytic_provider.event_repository()
    service = analytic_provider.event_ingestion_service(repository)

    await service.ingest({"type": "ConsultationStatusChanged", "consultation_id": "consult-1"}, "agenda.consultation.status")

    assert repository.items[0]["event_name"] == "ConsultationStatusChanged"
    assert repository.items[0]["source_service"] == "agenda-service"


@pytest.mark.asyncio
async def test_event_ingestion_service_falls_back_to_routing_key(analytic_provider):
    repository = analytic_provider.event_repository()
    service = analytic_provider.event_ingestion_service(repository)

    await service.ingest({"payload": {"id": "unknown"}}, "external.event.received")

    assert repository.items[0]["event_name"] == "external.event.received"
    assert repository.items[0]["source_service"] == "unknown"


def test_event_repository_limits_recent_results(analytic_provider):
    repository = analytic_provider.event_repository()

    repository.save({"event": "First"}, "users.first")
    repository.save({"event": "Second"}, "users.second")
    repository.save({"event": "Third"}, "users.third")

    assert [item["event_name"] for item in repository.list_recent(limit=2)] == ["Third", "Second"]
