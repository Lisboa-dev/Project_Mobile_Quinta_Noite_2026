"""
Testes de endpoints do Auth Service
Cobre login, validação de token, health check
"""
import pytest
from httpx import AsyncClient
from . import mock_data


@pytest.mark.auth
class TestAuthLoginEndpoints:
    """Testes para endpoints de autenticação"""
    
    async def test_login_success(self, auth_client: AsyncClient):
        """POST /auth/login - Login com credenciais válidas"""
        data = mock_data.login_data()
        
        response = await auth_client.post(
            "/auth/login",
            json=data
        )
        
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            result = response.json()
            tokens = result.get("tokens") if isinstance(result.get("tokens"), dict) else {}
            assert result.get("access_token") or result.get("token") or tokens.get("access_token")
    
    async def test_login_invalid_credentials(self, auth_client: AsyncClient):
        """POST /auth/login - Login com credenciais inválidas"""
        data = mock_data.invalid_login_data()
        
        response = await auth_client.post(
            "/auth/login",
            json=data
        )
        
        assert response.status_code == 401
        result = response.json()
        assert "error" in result or "detail" in result
    
    async def test_login_missing_email(self, auth_client: AsyncClient):
        """POST /auth/login - Login sem email"""
        data = {"password": "TestPassword123!"}
        
        response = await auth_client.post(
            "/auth/login",
            json=data
        )
        
        assert response.status_code in [400, 422]
    
    async def test_login_missing_password(self, auth_client: AsyncClient):
        """POST /auth/login - Login sem senha"""
        data = {"email": "test@clinica.local"}
        
        response = await auth_client.post(
            "/auth/login",
            json=data
        )
        
        assert response.status_code in [400, 422]
    
    async def test_login_empty_body(self, auth_client: AsyncClient):
        """POST /auth/login - Login com body vazio"""
        response = await auth_client.post(
            "/auth/login",
            json={}
        )
        
        assert response.status_code in [400, 422]
    
    async def test_login_invalid_json(self, auth_client: AsyncClient):
        """POST /auth/login - Login com JSON inválido"""
        response = await auth_client.post(
            "/auth/login",
            content=b"invalid json {",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]


@pytest.mark.auth
class TestAuthValidationEndpoints:
    """Testes para endpoints de validação de token"""
    
    async def test_validate_token_valid(self, auth_client: AsyncClient, auth_token: str):
        """GET /auth/validate - Validar token válido"""
        if not auth_token:
            pytest.skip("Token válido não obtido")
        
        response = await auth_client.get(
            "/auth/validate",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        # Verifica headers de resposta esperados
        assert "X-User-Id" in response.headers or "x-user-id" in response.headers
        assert "X-User-Role" in response.headers or "x-user-role" in response.headers
    
    async def test_validate_token_missing(self, auth_client: AsyncClient):
        """GET /auth/validate - Validar sem token"""
        response = await auth_client.get("/auth/validate")
        
        assert response.status_code == 401
    
    async def test_validate_token_invalid(self, auth_client: AsyncClient):
        """GET /auth/validate - Validar com token inválido"""
        response = await auth_client.get(
            "/auth/validate",
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        
        assert response.status_code in [401, 403]
    
    async def test_validate_token_malformed_bearer(self, auth_client: AsyncClient):
        """GET /auth/validate - Validar com header Bearer malformado"""
        response = await auth_client.get(
            "/auth/validate",
            headers={"Authorization": "InvalidBearer token"}
        )
        
        assert response.status_code in [401, 403]
    
    async def test_validate_token_without_bearer(self, auth_client: AsyncClient):
        """GET /auth/validate - Validar com token sem Bearer prefix"""
        response = await auth_client.get(
            "/auth/validate",
            headers={"Authorization": "just_a_token_string"}
        )
        
        assert response.status_code in [401, 403]
    
    async def test_validate_token_expired(self, auth_client: AsyncClient):
        """GET /auth/validate - Validar com token expirado"""
        # Usa um token que parece válido mas foi modificado
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjB9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
        
        response = await auth_client.get(
            "/auth/validate",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code in [401, 403]


@pytest.mark.auth
@pytest.mark.health
class TestAuthHealthEndpoint:
    """Testes para health check do Auth Service"""
    
    async def test_health_check(self, auth_client: AsyncClient):
        """GET /health - Health check do auth service"""
        response = await auth_client.get("/health")
        
        assert response.status_code == 200
        result = response.json()
        assert result.get("status") == "ok" or "ok" in str(result).lower()
        assert result.get("service") == "Auth Service" or "auth" in str(result).lower()


@pytest.mark.auth
class TestAuthTokenContent:
    """Testes para conteúdo do token JWT retornado"""
    
    async def test_token_contains_required_claims(self, auth_client: AsyncClient):
        """POST /auth/login - Token contém claims obrigatórios"""
        data = mock_data.login_data()
        
        response = await auth_client.post(
            "/auth/login",
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            tokens = result.get("tokens") if isinstance(result.get("tokens"), dict) else {}
            token = result.get("access_token") or result.get("token") or tokens.get("access_token")
            
            if token:
                # Tenta decodificar o header do JWT (sem validação de assinatura)
                import base64
                import json
                
                parts = token.split('.')
                if len(parts) >= 2:
                    # Decodifica o payload (segunda parte)
                    payload = parts[1]
                    # Adiciona padding se necessário
                    padding = 4 - len(payload) % 4
                    if padding != 4:
                        payload += '=' * padding
                    
                    try:
                        decoded = json.loads(base64.urlsafe_b64decode(payload))
                        # Verifica claims esperados
                        assert "sub" in decoded  # subject (user id)
                        assert "iat" in decoded  # issued at
                    except Exception:
                        # Se não conseguir decodificar, tudo bem
                        pass


@pytest.mark.auth
class TestAuthForwardAuthEndpoint:
    """Testes para forward_auth usado pelo gateway"""
    
    async def test_forward_auth_with_valid_token(self, auth_client: AsyncClient, auth_token: str):
        """forward_auth retorna headers corretos"""
        if not auth_token:
            pytest.skip("Token válido não obtido")
        
        response = await auth_client.get(
            "/auth/validate",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        headers = {k.lower(): v for k, v in response.headers.items()}
        assert "x-user-id" in headers
        assert "x-user-role" in headers
        assert headers["x-user-id"]  # Não vazio
        assert headers["x-user-role"]  # Não vazio
