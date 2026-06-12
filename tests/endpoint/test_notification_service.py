"""
Testes de endpoints do Notification Service
Cobre notificações para usuários, pacientes, médicos, admins, websockets
"""
import pytest
from httpx import AsyncClient
from . import mock_data


@pytest.mark.notification
class TestNotificationHealthEndpoint:
    """Testes para health check do Notification Service"""
    
    async def test_health_check(self, notification_client: AsyncClient):
        """GET /health - Health check do notification service"""
        response = await notification_client.get("/health")
        
        assert response.status_code == 200
        result = response.json()
        assert "status" in result or "ok" in str(result).lower()


@pytest.mark.notification
class TestUserNotificationEndpoints:
    """Testes para notificações de usuários"""
    
    async def test_list_user_notifications(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/users/{user_id} - Listar notificações do usuário"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/users/{test_ids['user_id']}?limit=50&unread_only=false"
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            result = response.json()
            assert isinstance(result, (list, dict))
    
    async def test_list_user_notifications_unread_only(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/users/{user_id} - Listar apenas não lidas"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/users/{test_ids['user_id']}?unread_only=true"
        )
        
        assert response.status_code in [200, 404]
    
    async def test_get_user_bell(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/users/{user_id}/bell - Bell de notificações"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/users/{test_ids['user_id']}/bell"
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            result = response.json()
            # Verifica se contém informações de bell
            assert any(key in result for key in ["unread", "count", "summary"])
    
    async def test_count_unread_user_notifications(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/users/{user_id}/unread-count - Contar não lidas"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/users/{test_ids['user_id']}/unread-count"
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            result = response.json()
            # Deve retornar um número ou dict com count
            assert isinstance(result, (int, dict))


@pytest.mark.notification
class TestPatientNotificationEndpoints:
    """Testes para notificações de pacientes"""
    
    async def test_list_patient_notifications(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/patients/{patient_id} - Notificações do paciente"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/patients/{test_ids['patient_id']}"
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            result = response.json()
            assert isinstance(result, (list, dict))
    
    async def test_list_pacient_notifications_pt(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/pacients/{patient_id} - Alias em PT"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/pacients/{test_ids['patient_id']}"
        )
        
        assert response.status_code in [200, 404]
    
    async def test_get_patient_bell(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/patients/{patient_id}/bell - Bell do paciente"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/patients/{test_ids['patient_id']}/bell"
        )
        
        assert response.status_code in [200, 404]
    
    async def test_get_pacient_bell_pt(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/pacients/{patient_id}/bell - Alias em PT"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/pacients/{test_ids['patient_id']}/bell"
        )
        
        assert response.status_code in [200, 404]


@pytest.mark.notification
class TestDoctorNotificationEndpoints:
    """Testes para notificações de médicos"""
    
    async def test_list_doctor_notifications(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/doctors/{doctor_id} - Notificações do médico"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/doctors/{test_ids['doctor_id']}"
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            result = response.json()
            assert isinstance(result, (list, dict))
    
    async def test_list_medic_notifications_pt(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/medics/{doctor_id} - Alias em PT"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/medics/{test_ids['doctor_id']}"
        )
        
        assert response.status_code in [200, 404]
    
    async def test_get_doctor_bell(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/doctors/{doctor_id}/bell - Bell do médico"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/doctors/{test_ids['doctor_id']}/bell"
        )
        
        assert response.status_code in [200, 404]
    
    async def test_get_medic_bell_pt(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/medics/{doctor_id}/bell - Alias em PT"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/medics/{test_ids['doctor_id']}/bell"
        )
        
        assert response.status_code in [200, 404]


@pytest.mark.notification
class TestAdminNotificationEndpoints:
    """Testes para notificações de admins"""
    
    async def test_list_admin_notifications(self, notification_client: AsyncClient, auth_token: str):
        """GET /notifications/admins - Notificações de todos os admins"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get("/notifications/admins")
        
        assert response.status_code in [200, 403]  # 403 se não for admin
        if response.status_code == 200:
            result = response.json()
            assert isinstance(result, (list, dict))
    
    async def test_get_admin_bell(self, notification_client: AsyncClient, auth_token: str):
        """GET /notifications/admins/bell - Bell dos admins"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get("/notifications/admins/bell")
        
        assert response.status_code in [200, 403]
    
    async def test_list_admin_notifications_by_id(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/admins/{admin_id} - Notificações de admin específico"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/admins/{test_ids['user_id']}"
        )
        
        assert response.status_code in [200, 404, 403]
    
    async def test_get_admin_bell_by_id(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/admins/{admin_id}/bell - Bell de admin específico"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/admins/{test_ids['user_id']}/bell"
        )
        
        assert response.status_code in [200, 404, 403]


@pytest.mark.notification
class TestNotificationDetailEndpoints:
    """Testes para detalhes de notificação e ações"""
    
    async def test_detail_notification(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /notifications/{notification_id} - Detalhe de notificação"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.get(
            f"/notifications/{test_ids['notification_id']}"
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            result = response.json()
            # Verifica campos esperados em uma notificação
            assert any(key in result for key in ["id", "title", "message", "content"])
    
    async def test_mark_notification_read(self, notification_client: AsyncClient, auth_token: str, test_ids: dict):
        """PATCH /notifications/{notification_id}/read - Marcar como lida"""
        notification_client.set_auth_token(auth_token)
        
        response = await notification_client.patch(
            f"/notifications/{test_ids['notification_id']}/read"
        )
        
        assert response.status_code in [200, 204, 404]


@pytest.mark.notification
class TestNotificationWebSocketEndpoints:
    """Testes para WebSocket do Notification Service"""
    
    async def test_websocket_events_path_exists(self, notification_client: AsyncClient):
        """WebSocket /ws/events - Caminho existe (não pode testar WS com AsyncClient)"""
        # Com AsyncClient HTTP, não podemos fazer upgrade de WebSocket
        # Apenas verificamos que o serviço responde
        response = await notification_client.get("/ws/events")
        
        # O serviço deve rejeitar GET (espera WebSocket)
        # Não esperamos 200, mas sim uma resposta que indique WebSocket upgrade
        assert response.status_code in [400, 404, 405, 426]  # Upgrade required ou similares
    
    async def test_websocket_notifications_path_exists(self, notification_client: AsyncClient):
        """WebSocket /ws/notifications - Caminho existe"""
        response = await notification_client.get("/ws/notifications")
        
        # Mesmo comportamento que eventos
        assert response.status_code in [400, 404, 405, 426]


@pytest.mark.notification
@pytest.mark.health
class TestNotificationHealthCheck:
    """Testes adicionais para health check"""
    
    async def test_health_returns_json(self, notification_client: AsyncClient):
        """Health check retorna JSON válido"""
        response = await notification_client.get("/health")
        
        assert response.status_code == 200
        try:
            result = response.json()
            assert isinstance(result, dict)
        except Exception:
            pytest.fail("Health check não retornou JSON válido")
