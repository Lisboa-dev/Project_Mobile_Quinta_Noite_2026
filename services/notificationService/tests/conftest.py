import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.router import router as api_router


@pytest.fixture
def sample_notification() -> dict:
    return {
        "id": "notification-1",
        "user_id": "user-1",
        "title": "Agenda atualizada",
        "message": "Sua consulta foi atualizada.",
        "channel": "bell",
        "link": "/agenda/apt-1",
        "read": False,
        "metadata": {"appointment_id": "apt-1"},
        "created_at": "2026-06-08T10:00:00Z",
    }


class FakeNotificationRepository:
    def __init__(self, items: list[dict] | None = None) -> None:
        self.items = items or []
        self.created: list[dict] = []

    def create(self, notification: dict) -> dict:
        persisted = {**notification, "read": False, "created_at": "2026-06-08T10:00:00Z"}
        self.created.append(notification)
        self.items.append(persisted)
        return persisted

    def list_by_user(self, user_id: str, limit: int = 50, unread_only: bool = False) -> list[dict]:
        items = [item for item in self.items if item["user_id"] == user_id]
        if unread_only:
            items = [item for item in items if not item["read"]]
        return items[:limit]

    def mark_read(self, notification_id: str) -> dict | None:
        for item in self.items:
            if item["id"] == notification_id:
                item["read"] = True
                return item
        return None

    def get(self, notification_id: str) -> dict | None:
        for item in self.items:
            if item["id"] == notification_id:
                return item
        return None

    def count_unread(self, user_id: str) -> int:
        return len([item for item in self.items if item["user_id"] == user_id and not item["read"]])


class FakeWebSocketHub:
    def __init__(self) -> None:
        self.payloads: list[dict] = []

    async def broadcast(self, payload: dict) -> None:
        self.payloads.append(payload)


class FakeNotificationQueryService:
    def __init__(self, repository: FakeNotificationRepository) -> None:
        self.repository = repository

    def list_by_user(self, user_id: str, limit: int = 50, unread_only: bool = False) -> list[dict]:
        return self.repository.list_by_user(user_id=user_id, limit=limit, unread_only=unread_only)

    def mark_read(self, notification_id: str) -> dict | None:
        return self.repository.mark_read(notification_id)

    def count_unread(self, user_id: str) -> int:
        return self.repository.count_unread(user_id)

    def detail(self, notification_id: str) -> dict | None:
        return self.repository.get(notification_id)

    def bell(self, user_id: str) -> dict:
        latest = self.repository.list_by_user(user_id=user_id, limit=5, unread_only=True)
        unread = self.repository.count_unread(user_id)
        return {"user_id": user_id, "has_new": unread > 0, "unread": unread, "latest": latest}


@pytest.fixture
def fake_repository(sample_notification) -> FakeNotificationRepository:
    return FakeNotificationRepository(items=[sample_notification.copy()])


@pytest.fixture
def fake_hub() -> FakeWebSocketHub:
    return FakeWebSocketHub()


@pytest.fixture
def api_client(fake_repository) -> TestClient:
    app = FastAPI()
    app.state.notification_query_service = FakeNotificationQueryService(fake_repository)
    app.include_router(api_router)
    return TestClient(app)
