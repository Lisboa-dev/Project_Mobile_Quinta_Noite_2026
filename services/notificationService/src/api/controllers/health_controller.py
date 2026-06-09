from fastapi import APIRouter

from src.infra.websocket import events_hub, notifications_hub

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "websocket": {
            "events": events_hub.snapshot(),
            "notifications": notifications_hub.snapshot(),
        },
    }
