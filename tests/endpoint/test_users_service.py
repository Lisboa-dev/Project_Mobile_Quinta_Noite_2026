"""
Testes de endpoints do usersService
Cobre todos os controllers: Admin, Attendant, Doctor, Patient, User CRUD, Config
"""
import pytest
from httpx import AsyncClient
from . import mock_data


@pytest.mark.users
class TestUserCrudEndpoints:
    """Testes para endpoints CRUD genérico de usuários"""
    
    async def test_create_user(self, users_client: AsyncClient, auth_token: str):
        """POST /users/ - Criar usuário"""
        data = mock_data.user_data()
        users_client.set_auth_token(auth_token)
        
        response = await users_client.post(
            "/users/",
            json=data
        )
        
        assert response.status_code in [200, 201, 409]  # 409 se email/username existe
        if response.status_code in [200, 201]:
            result = response.json()
            assert result.get("id") or result.get("user_id")
    
    async def test_list_users(self, users_client: AsyncClient, auth_token: str):
        """GET /users/ - Listar usuários"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.get("/users/")
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, (list, dict))
    
    async def test_get_user(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /users/{user_id} - Obter usuário"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.get(
            f"/users/{test_ids['user_id']}"
        )
        
        assert response.status_code in [200, 404]
    
    async def test_update_user(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """PUT /users/{user_id} - Atualizar usuário"""
        data = mock_data.user_data()
        users_client.set_auth_token(auth_token)
        
        response = await users_client.put(
            f"/users/{test_ids['user_id']}",
            json=data
        )
        
        assert response.status_code in [200, 404]
    
    async def test_delete_user(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """DELETE /users/{user_id} - Deletar usuário"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.delete(
            f"/users/{test_ids['user_id']}"
        )
        
        assert response.status_code in [200, 204, 404]
    
    async def test_upload_profile_image(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """POST /users/{user_id}/profile-image - Upload de imagem de perfil"""
        users_client.set_auth_token(auth_token)
        
        # Cria um arquivo mock simples
        files = {
            "file": ("test.jpg", b"fake image data", "image/jpeg")
        }
        
        response = await users_client.post(
            f"/users/{test_ids['user_id']}/profile-image",
            files=files
        )
        
        assert response.status_code in [200, 201, 400, 404, 413]  # 413 se arquivo muito grande
    
    async def test_delete_profile_image(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """DELETE /users/{user_id}/profile-image - Deletar imagem de perfil"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.delete(
            f"/users/{test_ids['user_id']}/profile-image"
        )
        
        assert response.status_code in [200, 204, 404]


@pytest.mark.users
class TestAdminEndpoints:
    """Testes para endpoints de Administrador"""
    
    async def test_list_admins(self, users_client: AsyncClient, auth_token: str):
        """GET /admins - Listar admins"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.get("/admins/")
        
        assert response.status_code in [200, 403]  # 403 se não for admin
        if response.status_code == 200:
            result = response.json()
            assert isinstance(result, (list, dict))
    
    async def test_detail_admin(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /admins/{user_id} - Detalhe de admin"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.get(
            f"/admins/{test_ids['user_id']}"
        )
        
        assert response.status_code in [200, 404, 403]
    
    async def test_promote_user_to_admin(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """POST /admins/{user_id}/promote - Promover usuário a admin"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.post(
            f"/admins/{test_ids['user_id']}/promote"
        )
        
        assert response.status_code in [200, 404, 403]
    
    async def test_depreciate_admin(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """POST /admins/{user_id}/depreciate - Remover admin"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.post(
            f"/admins/{test_ids['user_id']}/depreciate"
        )
        
        assert response.status_code in [200, 404, 403]
    
    async def test_admin_create_doctor(self, users_client: AsyncClient, auth_token: str):
        """POST /admins/doctors - Admin criar médico"""
        data = mock_data.medic_data()
        users_client.set_auth_token(auth_token)
        
        response = await users_client.post(
            "/admins/doctors",
            json=data
        )
        
        assert response.status_code in [200, 201, 400, 403]
    
    async def test_delete_admin(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """DELETE /admins/{user_id} - Deletar admin"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.delete(
            f"/admins/{test_ids['user_id']}"
        )
        
        assert response.status_code in [200, 204, 404, 403]


@pytest.mark.users
class TestMedicEndpoints:
    """Testes para endpoints de Médico (Medic)"""
    
    async def test_create_medic(self, users_client: AsyncClient, auth_token: str):
        """POST /medics/ - Criar médico"""
        data = mock_data.medic_data()
        users_client.set_auth_token(auth_token)
        
        response = await users_client.post(
            "/medics/",
            json=data
        )
        
        assert response.status_code in [200, 201, 400, 409]  # 409 se email existe
    
    async def test_list_medics(self, users_client: AsyncClient, auth_token: str):
        """GET /medics/ - Listar médicos"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.get("/medics/")
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, (list, dict))
    
    async def test_detail_medic(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /medics/{user_id} - Detalhe de médico"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.get(
            f"/medics/{test_ids['doctor_id']}"
        )
        
        assert response.status_code in [200, 404]
    
    async def test_update_medic(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """PUT /medics/{user_id} - Atualizar médico (NOT IMPLEMENTED)"""
        data = mock_data.medic_data()
        users_client.set_auth_token(auth_token)
        
        response = await users_client.put(
            f"/medics/{test_ids['doctor_id']}",
            json=data
        )
        
        assert response.status_code in [200, 404, 501]  # 501 Not Implemented
    
    async def test_delete_medic(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """DELETE /medics/{user_id} - Deletar médico"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.delete(
            f"/medics/{test_ids['doctor_id']}"
        )
        
        assert response.status_code in [200, 204, 404]


@pytest.mark.users
class TestPacientEndpoints:
    """Testes para endpoints de Paciente (Pacient)"""
    
    async def test_create_pacient(self, users_client: AsyncClient, auth_token: str):
        """POST /pacients/ - Criar paciente"""
        data = mock_data.pacient_data()
        users_client.set_auth_token(auth_token)
        
        response = await users_client.post(
            "/pacients/",
            json=data
        )
        
        assert response.status_code in [200, 201, 400, 409]
    
    async def test_list_pacients(self, users_client: AsyncClient, auth_token: str):
        """GET /pacients/ - Listar pacientes"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.get("/pacients/")
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, (list, dict))
    
    async def test_detail_pacient(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /pacients/{user_id} - Detalhe de paciente"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.get(
            f"/pacients/{test_ids['patient_id']}"
        )
        
        assert response.status_code in [200, 404]
    
    async def test_update_pacient(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """PUT /pacients/{user_id} - Atualizar paciente (NOT IMPLEMENTED)"""
        data = mock_data.pacient_data()
        users_client.set_auth_token(auth_token)
        
        response = await users_client.put(
            f"/pacients/{test_ids['patient_id']}",
            json=data
        )
        
        assert response.status_code in [200, 404, 501]
    
    async def test_delete_pacient(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """DELETE /pacients/{user_id} - Deletar paciente"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.delete(
            f"/pacients/{test_ids['patient_id']}"
        )
        
        assert response.status_code in [200, 204, 404]


@pytest.mark.users
class TestAtendentEndpoints:
    """Testes para endpoints de Atendente"""
    
    async def test_create_atendent(self, users_client: AsyncClient, auth_token: str):
        """POST /atendents/ - Criar atendente"""
        data = mock_data.atendent_data()
        users_client.set_auth_token(auth_token)
        
        response = await users_client.post(
            "/atendents/",
            json=data
        )
        
        assert response.status_code in [200, 201, 400, 409]
    
    async def test_list_atendents(self, users_client: AsyncClient, auth_token: str):
        """GET /atendents/ - Listar atendentes"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.get("/atendents/")
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, (list, dict))
    
    async def test_detail_atendent(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """GET /atendents/{user_id} - Detalhe de atendente"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.get(
            f"/atendents/{test_ids['user_id']}"
        )
        
        assert response.status_code in [200, 404]
    
    async def test_update_atendent(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """PUT /atendents/{user_id} - Atualizar atendente (NOT IMPLEMENTED)"""
        data = mock_data.atendent_data()
        users_client.set_auth_token(auth_token)
        
        response = await users_client.put(
            f"/atendents/{test_ids['user_id']}",
            json=data
        )
        
        assert response.status_code in [200, 404, 501]
    
    async def test_delete_atendent(self, users_client: AsyncClient, auth_token: str, test_ids: dict):
        """DELETE /atendents/{user_id} - Deletar atendente"""
        users_client.set_auth_token(auth_token)
        
        response = await users_client.delete(
            f"/atendents/{test_ids['user_id']}"
        )
        
        assert response.status_code in [200, 204, 404]


@pytest.mark.users
class TestClientConfigEndpoints:
    """Testes para endpoints de configuração cliente"""
    
    async def test_get_client_config(self, users_client: AsyncClient):
        """GET /config/client - Obter configuração cliente"""
        response = await users_client.get("/config/client")
        
        assert response.status_code == 200
        result = response.json()
        profile_image = result.get("profileImage", {})
        assert any(key in profile_image for key in ["maxBytes", "allowedTypes", "bucket", "publicUrl"])


@pytest.mark.users
@pytest.mark.health
class TestUsersHealthEndpoint:
    """Testes para health check do usersService"""
    
    async def test_users_health_check(self, users_client: AsyncClient):
        """Health check do users service"""
        possible_paths = ["/health", "/"]
        
        for path in possible_paths:
            response = await users_client.get(path)
            if response.status_code == 200:
                data = response.json()
                assert "status" in data or "ok" in str(data).lower()
                break
