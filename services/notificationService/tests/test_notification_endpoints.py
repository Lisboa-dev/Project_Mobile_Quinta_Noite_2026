def test_health_endpoint_returns_status_and_websocket_snapshot(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "websocket" in response.json()


def test_list_user_notifications(api_client):
    response = api_client.get("/notifications/users/user-1")

    assert response.status_code == 200
    assert response.json()[0]["id"] == "notification-1"


def test_list_user_notifications_supports_unread_filter(api_client, fake_repository):
    fake_repository.items[0]["read"] = True

    response = api_client.get("/notifications/users/user-1?unread_only=true")

    assert response.status_code == 200
    assert response.json() == []


def test_list_user_notifications_validates_limit(api_client):
    response = api_client.get("/notifications/users/user-1?limit=0")

    assert response.status_code == 422


def test_count_unread_user_notifications(api_client):
    response = api_client.get("/notifications/users/user-1/unread-count")

    assert response.status_code == 200
    assert response.json() == {"user_id": "user-1", "unread": 1}


def test_user_bell_returns_unread_state(api_client):
    response = api_client.get("/notifications/users/user-1/bell")

    assert response.status_code == 200
    assert response.json()["has_new"] is True
    assert response.json()["unread"] == 1
    assert response.json()["latest"][0]["id"] == "notification-1"


def test_patient_bell_and_list_use_patient_id(api_client, fake_repository, sample_notification):
    fake_repository.items.append({**sample_notification, "id": "patient-notification", "user_id": "patient-1"})

    bell = api_client.get("/notifications/patients/patient-1/bell")
    listing = api_client.get("/notifications/patients/patient-1")

    assert bell.status_code == 200
    assert bell.json()["has_new"] is True
    assert listing.json()[0]["id"] == "patient-notification"


def test_medic_bell_and_list_use_doctor_id(api_client, fake_repository, sample_notification):
    fake_repository.items.append({**sample_notification, "id": "doctor-notification", "user_id": "doctor-1"})

    bell = api_client.get("/notifications/medics/doctor-1/bell")
    listing = api_client.get("/notifications/medics/doctor-1")

    assert bell.status_code == 200
    assert bell.json()["unread"] == 1
    assert listing.json()[0]["id"] == "doctor-notification"


def test_admin_bell_and_list_use_global_admin_channel(api_client, fake_repository, sample_notification):
    fake_repository.items.append({**sample_notification, "id": "admin-notification", "user_id": "admin"})

    bell = api_client.get("/notifications/admins/bell")
    listing = api_client.get("/notifications/admins")

    assert bell.status_code == 200
    assert bell.json()["user_id"] == "admin"
    assert listing.json()[0]["id"] == "admin-notification"


def test_detail_notification(api_client):
    response = api_client.get("/notifications/notification-1")

    assert response.status_code == 200
    assert response.json()["id"] == "notification-1"


def test_detail_unknown_notification_returns_404(api_client):
    response = api_client.get("/notifications/missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"


def test_mark_notification_read(api_client):
    response = api_client.patch("/notifications/notification-1/read")

    assert response.status_code == 200
    assert response.json()["read"] is True


def test_mark_unknown_notification_returns_404(api_client):
    response = api_client.patch("/notifications/missing/read")

    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"


def test_websocket_events_connects(api_client):
    with api_client.websocket_connect("/ws/events") as websocket:
        websocket.send_text("ping")


def test_websocket_notifications_connects(api_client):
    with api_client.websocket_connect("/ws/notifications") as websocket:
        websocket.send_text("ping")
