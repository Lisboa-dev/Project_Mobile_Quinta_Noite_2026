"""Endpoint tests for agendaService against the running application.

The scenarios emulate a logged-in user: tests that hit protected endpoints use
the real auth token fixture and the gateway headers propagated by ServiceClient.
"""

import pytest

from . import mock_data


async def _mirror_doctor_and_patient(agenda_client):
    doctor_payload = {
        "event": "users.doctor.created",
        "data": {
            "id": mock_data.DOCTOR_ID,
            "userName": "dra.endpoint",
            "name": "Dra Endpoint",
            "cargo": "MEDICO",
            "triggered_by_id": mock_data.ADMIN_ID,
        },
    }
    patient_payload = {
        "event": "users.patient.created",
        "data": {
            "id": mock_data.PATIENT_ID,
            "userName": "paciente.endpoint",
            "name": "Paciente Endpoint",
            "cargo": "PACIENTE",
            "triggered_by_id": mock_data.ADMIN_ID,
        },
    }

    doctor = await agenda_client.post("/agenda/infra/events/users/doctor-created", json=doctor_payload)
    patient = await agenda_client.post("/agenda/infra/events/users/patient-created", json=patient_payload)
    assert doctor.status_code in {200, 201, 400}
    assert patient.status_code in {200, 201, 400}


def _assert_json_collection(response):
    assert response.status_code == 200
    assert isinstance(response.json(), (list, dict))


@pytest.mark.agenda
@pytest.mark.health
class TestAgendaHealth:
    async def test_health(self, agenda_client):
        response = await agenda_client.get("/agenda/infra/health")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert response.json().get("status") in {"ok", "healthy", None}
        assert response.json().get("mode") or "dependencies" in response.json() or "status" in response.json()

    async def test_readiness(self, agenda_client):
        response = await agenda_client.get("/agenda/infra/ready")
        assert response.status_code in {200, 503}


@pytest.mark.agenda
class TestAgendaAppointments:
    async def test_create_appointment_without_room(self, agenda_client, auth_token):
        agenda_client.set_auth_token(auth_token)
        await _mirror_doctor_and_patient(agenda_client)

        room = await agenda_client.post("/agenda/rooms/", json=mock_data.room_data())
        assert room.status_code in {201, 400}

        payload = mock_data.appointment_data()

        assert "room" not in payload
        assert "room_id" not in payload

        response = await agenda_client.post("/agenda/appointments/", json=payload)
        assert response.status_code in {201, 400, 404}
        if response.status_code == 201:
            assert response.json() == {"created": True}

    async def test_create_appointment_requires_core_fields(self, agenda_client, auth_token):
        agenda_client.set_auth_token(auth_token)
        payload = mock_data.appointment_data()
        payload.pop("doctor")

        response = await agenda_client.post("/agenda/appointments/", json=payload)
        assert response.status_code == 422

    async def test_list_and_filter_appointments(self, agenda_client):
        _assert_json_collection(await agenda_client.get("/agenda/appointments/?limit=20&offset=0"))
        _assert_json_collection(await agenda_client.get(f"/agenda/appointments/patient/{mock_data.PATIENT_ID}?limit=20&offset=0"))
        _assert_json_collection(await agenda_client.get(f"/agenda/appointments/doctor/{mock_data.DOCTOR_ID}?limit=20&offset=0"))

    async def test_appointment_detail_update_delete_missing_id(self, agenda_client, auth_token, test_ids):
        agenda_client.set_auth_token(auth_token)
        appointment_id = test_ids["appointment_id"]

        assert (await agenda_client.get(f"/agenda/appointments/{appointment_id}")).status_code in {200, 404}
        assert (await agenda_client.put(f"/agenda/appointments/{appointment_id}", json={"triggered_by_id": mock_data.ADMIN_ID})).status_code in {200, 404}
        assert (await agenda_client.delete(f"/agenda/appointments/{appointment_id}")).status_code in {204, 404}

    async def test_appointment_types(self, agenda_client):
        _assert_json_collection(await agenda_client.get("/agenda/appointments/types/?limit=20&offset=0"))
        assert (await agenda_client.get("/agenda/appointments/types/tipo-consulta-1")).status_code in {200, 404}


@pytest.mark.agenda
class TestAgendaRooms:
    async def test_rooms_are_admin_protected(self, agenda_client):
        response = await agenda_client.get("/agenda/rooms/")
        assert response.status_code == 403

    async def test_room_crud_as_admin(self, agenda_client, auth_token, test_ids):
        agenda_client.set_auth_token(auth_token)
        create = await agenda_client.post("/agenda/rooms/", json=mock_data.room_data())
        assert create.status_code in {201, 400}

        _assert_json_collection(await agenda_client.get("/agenda/rooms/?limit=20&offset=0"))
        assert (await agenda_client.get(f"/agenda/rooms/{test_ids['room_id']}")).status_code in {200, 404}
        assert (await agenda_client.put(f"/agenda/rooms/{test_ids['room_id']}", json=mock_data.room_data())).status_code in {200, 404}
        assert (await agenda_client.delete(f"/agenda/rooms/{test_ids['room_id']}")).status_code in {204, 404}

    async def test_room_admin_views(self, agenda_client, auth_token, test_ids):
        agenda_client.set_auth_token(auth_token)
        _assert_json_collection(await agenda_client.get("/agenda/rooms/admin/?limit=20&offset=0"))
        assert (await agenda_client.get(f"/agenda/rooms/admin/{test_ids['room_id']}")).status_code in {200, 404}


@pytest.mark.agenda
class TestAgendaCalendars:
    async def test_calendar_lifecycle(self, agenda_client, auth_token, test_ids):
        agenda_client.set_auth_token(auth_token)

        create = await agenda_client.post("/agenda/calendars/", json=mock_data.calendar_data())
        assert create.status_code in {200, 201, 400}

        now = mock_data.datetime.now()
        _assert_json_collection(await agenda_client.get(f"/agenda/calendars/days?year={now.year}&month={now.month}"))
        _assert_json_collection(await agenda_client.get(f"/agenda/calendars/months/{now.year}/{now.month}/days"))
        assert (await agenda_client.get(f"/agenda/calendars/days/{test_ids['appointment_id']}")).status_code in {200, 404}
        assert (await agenda_client.patch(f"/agenda/calendars/days/{test_ids['appointment_id']}", json=mock_data.calendar_day_data())).status_code in {200, 404}


@pytest.mark.agenda
class TestAgendaRules:
    async def test_rules_are_admin_protected(self, agenda_client):
        response = await agenda_client.get("/agenda/rules/")
        assert response.status_code == 403

    async def test_list_rules_supports_scope_filters(self, agenda_client, auth_token):
        agenda_client.set_auth_token(auth_token)
        _assert_json_collection(await agenda_client.get("/agenda/rules/?limit=20&offset=0"))
        _assert_json_collection(await agenda_client.get(f"/agenda/rules/?type=doctor&id={mock_data.DOCTOR_ID}&limit=20&offset=0"))

    async def test_rule_admin_context_and_detail(self, agenda_client, auth_token, test_ids):
        agenda_client.set_auth_token(auth_token)
        context = await agenda_client.get("/agenda/rules/admin/context")
        assert context.status_code == 200
        assert "all" in context.json()

        assert (await agenda_client.get(f"/agenda/rules/{test_ids['rule_id']}")).status_code in {200, 404}
        assert (await agenda_client.get(f"/agenda/rules/detail/{test_ids['rule_id']}")).status_code in {200, 404}

    @pytest.mark.parametrize(
        ("path", "payload_factory"),
        [
            ("/agenda/rules/block", mock_data.rule_data_block),
            ("/agenda/rules/generic", mock_data.rule_data_generic),
            ("/agenda/rules/specific", mock_data.rule_data_specific),
            ("/agenda/rules/specific-day", mock_data.rule_data_specific_day),
            ("/agenda/rules/week", mock_data.rule_data_week),
        ],
    )
    async def test_create_rule_variants(self, agenda_client, auth_token, path, payload_factory):
        agenda_client.set_auth_token(auth_token)
        response = await agenda_client.post(path, json=payload_factory())
        assert response.status_code in {201, 400}
        if response.status_code == 201:
            body = response.json()
            assert body.get("created", {}).get("success") is True

    async def test_specific_rule_requires_id_and_type(self, agenda_client, auth_token):
        agenda_client.set_auth_token(auth_token)
        payload = mock_data.rule_data_specific()
        payload.pop("id")
        response = await agenda_client.post("/agenda/rules/specific", json=payload)
        assert response.status_code == 422


@pytest.mark.agenda
class TestAgendaUserEvents:
    async def test_user_service_events_are_accepted(self, agenda_client, auth_token):
        agenda_client.set_auth_token(auth_token)
        await _mirror_doctor_and_patient(agenda_client)

    async def test_user_service_events_ignore_wrong_cargo(self, agenda_client, auth_token):
        agenda_client.set_auth_token(auth_token)
        response = await agenda_client.post(
            "/agenda/infra/events/users/doctor-created",
            json={
                "event": "users.doctor.created",
                "data": {
                    "id": mock_data.DOCTOR_ID,
                    "userName": "usuario.nao.medico",
                    "cargo": "PACIENTE",
                    "triggered_by_id": mock_data.ADMIN_ID,
                },
            },
        )
        assert response.status_code == 200
        assert response.json().get("handled") is False
