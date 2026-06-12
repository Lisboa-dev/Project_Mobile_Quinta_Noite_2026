from fastapi import APIRouter, Query, Request, Response
from fastapi.encoders import jsonable_encoder

from src.services import EventIngestionService

router = APIRouter()


def get_service(request: Request) -> EventIngestionService:
    return request.app.state.event_ingestion_service


@router.get("/analytics/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/analytics/events", tags=["events"])
def list_events(request: Request, limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
    return jsonable_encoder(get_service(request).list_recent(limit=limit))


@router.get("/analytics/events/summary", tags=["events"])
def summarize_events(request: Request) -> list[dict]:
    return jsonable_encoder(get_service(request).count_by_source())


@router.get("/analytics/metrics", tags=["metrics"])
def metrics(request: Request) -> Response:
    metrics_registry = getattr(request.app.state, "http_metrics", None)
    content = metrics_registry.render() if metrics_registry is not None else ""
    return Response(content, media_type="text/plain; version=0.0.4")
