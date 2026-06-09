import pytest


@pytest.mark.asyncio
async def test_event_ingestion_saves_user_event(analytic_provider):
    repository = analytic_provider.event_repository()
    service = analytic_provider.event_ingestion_service(repository)

    await service.ingest({"event": "DoctorCreatedEvent", "doctor_id": "doctor-1"}, "users.doctor.created")

    assert repository.items[0]["source_service"] == "users-service"
    assert repository.items[0]["event_name"] == "DoctorCreatedEvent"
    assert repository.items[0]["payload"]["doctor_id"] == "doctor-1"


def test_event_ingestion_lists_recent_events(analytic_provider):
    repository = analytic_provider.event_repository()
    service = analytic_provider.event_ingestion_service(repository)

    repository.save({"event": "OlderEvent"}, "agenda.consultation.created")
    repository.save({"event": "NewerEvent"}, "users.doctor.created")

    recent = service.list_recent(limit=1)

    assert len(recent) == 1
    assert recent[0]["event_name"] == "NewerEvent"


def test_event_ingestion_counts_by_source(analytic_provider):
    repository = analytic_provider.event_repository()
    service = analytic_provider.event_ingestion_service(repository)

    repository.save({"event": "ConsultationCreatedEvent"}, "agenda.consultation.created")
    repository.save({"event": "DoctorCreatedEvent"}, "users.doctor.created")
    repository.save({"event": "DoctorUpdatedEvent"}, "users.doctor.updated")

    totals = service.count_by_source()

    assert totals == [
        {"source_service": "agenda-service", "total": 1},
        {"source_service": "users-service", "total": 2},
    ]
