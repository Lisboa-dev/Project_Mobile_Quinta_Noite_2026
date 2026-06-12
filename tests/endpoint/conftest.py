"""
Configuração e fixtures para testes de endpoints dos services.
Fornece clients HTTP para cada service com autenticação real, health checks e retry logic.
Simula chamadas reais do frontend (xxclient) para o backend.
"""
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from typing import Optional, Dict, Any
import asyncio
import time
import random
import string


# Base URLs dos services (pode ser customizado via env vars)
SERVICE_URLS = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://localhost:8000"),
    "agenda": os.getenv("AGENDA_SERVICE_URL", "http://localhost:8001"),
    "users": os.getenv("USERS_SERVICE_URL", "http://localhost:8002"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8003"),
    "analytic": os.getenv("ANALYTIC_SERVICE_URL", "http://localhost:8005"),
}

HEALTH_PATHS = {
    "auth": ["/health"],
    "agenda": ["/agenda/infra/health", "/health"],
    "users": ["/health"],
    "notification": ["/health"],
    "analytic": ["/analytics/health", "/health"],
}

# Configuração de retry
MAX_RETRIES = 5
RETRY_DELAY = 2  # segundos
TIMEOUT = 30.0  # segundos para requisições


class ServiceClient:
    """Cliente HTTP para um service específico com suporte a retry e autenticação"""
    
    def __init__(self, base_url: str, service_name: str):
        self.base_url = base_url
        self.service_name = service_name
        self.client: Optional[AsyncClient] = None
        self.auth_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.user_role: Optional[str] = None
        self._is_healthy = False
    
    async def __aenter__(self):
        self.client = AsyncClient(base_url=self.base_url, timeout=TIMEOUT)
        await self.check_health()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def check_health(self) -> bool:
        """Verifica se o service está saudável com retry"""
        for attempt in range(MAX_RETRIES):
            try:
                paths = HEALTH_PATHS.get(self.service_name, ["/health", "/api/health", "/_health"])
                
                for path in paths:
                    try:
                        response = await self.client.get(path, timeout=5.0)
                        if response.status_code == 200:
                            self._is_healthy = True
                            print(f"✓ {self.service_name} health check: OK")
                            return True
                    except:
                        continue
                
                # Se falhou, aguarda antes de retry
                if attempt < MAX_RETRIES - 1:
                    print(f"⏳ {self.service_name} não está pronto. Tentativa {attempt + 1}/{MAX_RETRIES}...")
                    await asyncio.sleep(RETRY_DELAY)
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
        
        raise ConnectionError(
            f"Service '{self.service_name}' não respondeu após {MAX_RETRIES} tentativas. "
            f"URL: {self.base_url}. Verifique se os services estão rodando: docker compose up -d"
        )
    
    @property
    def is_healthy(self) -> bool:
        return self._is_healthy
    
    async def get(self, path: str, **kwargs):
        """GET request com suporte a auth e retry"""
        return await self._request("GET", path, **kwargs)
    
    async def post(self, path: str, **kwargs):
        """POST request com suporte a auth e retry"""
        return await self._request("POST", path, **kwargs)
    
    async def put(self, path: str, **kwargs):
        """PUT request com suporte a auth e retry"""
        return await self._request("PUT", path, **kwargs)
    
    async def patch(self, path: str, **kwargs):
        """PATCH request com suporte a auth e retry"""
        return await self._request("PATCH", path, **kwargs)
    
    async def delete(self, path: str, **kwargs):
        """DELETE request com suporte a auth e retry"""
        return await self._request("DELETE", path, **kwargs)
    
    async def _request(self, method: str, path: str, retry_count: int = 0, **kwargs):
        """Executa request com headers de auth e retry automático"""
        try:
            # Adiciona auth token se disponível
            if self.auth_token:
                if "headers" not in kwargs:
                    kwargs["headers"] = {}
                kwargs["headers"]["Authorization"] = f"Bearer {self.auth_token}"
                if self.user_id:
                    kwargs["headers"]["X-User-Id"] = self.user_id
                if self.user_role:
                    kwargs["headers"]["X-User-Role"] = self.user_role
            
            response = await self.client.request(method, path, **kwargs)
            
            # Log da requisição para debug
            print(f"→ {method} {path} → {response.status_code}")
            
            return response
        
        except Exception as e:
            if retry_count < 2:
                print(f"⚠️  Erro na requisição, retrying... ({retry_count + 1}/3)")
                await asyncio.sleep(1)
                return await self._request(method, path, retry_count=retry_count + 1, **kwargs)
            raise
    
    def set_auth_token(self, token: str, user_id: str = None, user_role: str = None):
        """Define token JWT e informações do usuário para requisições autenticadas"""
        self.auth_token = token
        self.user_id = str(user_id or self.user_id or "550e8400-e29b-41d4-a716-446655440000")
        self.user_role = str(user_role or self.user_role or "admin").lower()
    
    def clear_auth(self):
        """Limpa autenticação"""
        self.auth_token = None
        self.user_id = None
        self.user_role = None


@pytest_asyncio.fixture
async def agenda_client():
    """Client para agendaService"""
    async with ServiceClient(SERVICE_URLS["agenda"], "agenda") as client:
        yield client


@pytest_asyncio.fixture
async def analytic_client():
    """Client para analyticService"""
    async with ServiceClient(SERVICE_URLS["analytic"], "analytic") as client:
        yield client


@pytest_asyncio.fixture
async def auth_client():
    """Client para auth service"""
    async with ServiceClient(SERVICE_URLS["auth"], "auth") as client:
        yield client


@pytest_asyncio.fixture
async def notification_client():
    """Client para notificationService"""
    async with ServiceClient(SERVICE_URLS["notification"], "notification") as client:
        yield client


@pytest_asyncio.fixture
async def users_client():
    """Client para usersService"""
    async with ServiceClient(SERVICE_URLS["users"], "users") as client:
        yield client


@pytest_asyncio.fixture
async def auth_token(auth_client):
    """Obtém token JWT válido para testes autenticados"""
    response = await auth_client.post(
        "/auth/login",
        json={
            "email": "admin@clinica.local",
            "password": "Admin123!"
        }
    )
    if response.status_code == 200:
        data = response.json()
        tokens = data.get("tokens") if isinstance(data.get("tokens"), dict) else {}
        token = data.get("access_token") or data.get("token") or tokens.get("access_token")
        user_id = str(data.get("user_id") or "")
        user_role = "admin"
        if token:
            # Extrai user_id do payload JWT (sem validação de assinatura)
            try:
                import base64
                import json
                parts = token.split('.')
                if len(parts) >= 2:
                    payload = parts[1]
                    padding = 4 - len(payload) % 4
                    if padding != 4:
                        payload += '=' * padding
                    decoded = json.loads(base64.urlsafe_b64decode(payload))
                    user_id = str(decoded.get("sub") or user_id)
                    user_role = str(decoded.get("role") or user_role)
                    auth_client.set_auth_token(token, user_id, user_role)
            except:
                pass
        return token
    return None


class AuthenticatedSession:
    """Sessão autenticada de usuário para simular cliente real"""
    
    def __init__(self, clients: Dict[str, ServiceClient], token: str, user_id: str, user_role: str):
        self.clients = clients
        self.token = token
        self.user_id = user_id
        self.user_role = user_role
        self.created_entities: Dict[str, list] = {
            "users": [],
            "clinics": [],
            "doctors": [],
            "patients": [],
            "appointments": [],
            "rooms": [],
        }
    
    async def setup(self):
        """Configura todos os clients com o token"""
        for client in self.clients.values():
            client.set_auth_token(self.token, self.user_id, self.user_role)
    
    def track_entity(self, entity_type: str, entity_id: str):
        """Rastreia entidades criadas para cleanup"""
        if entity_type in self.created_entities:
            self.created_entities[entity_type].append(entity_id)
    
    async def cleanup(self):
        """Limpa entidades criadas durante o teste (cleanup)"""
        print(f"\n🧹 Limpando entidades criadas...")
        # Adicionar lógica de cleanup conforme necessário


@pytest_asyncio.fixture
async def authenticated_session(auth_token, agenda_client, users_client, auth_client, notification_client, analytic_client):
    """Cria uma sessão autenticada com todos os clients preparados"""
    if not auth_token:
        pytest.skip("Falha ao autenticar")
    
    # Extrai informações do token
    try:
        import base64
        import json
        parts = auth_token.split('.')
        if len(parts) >= 2:
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            user_id = decoded.get("sub")
            user_role = decoded.get("role", "admin")
            if user_role:
                user_role = str(user_role).lower()
    except:
        user_id = "unknown"
        user_role = "admin"
    
    clients = {
        "agenda": agenda_client,
        "users": users_client,
        "auth": auth_client,
        "notification": notification_client,
        "analytic": analytic_client,
    }
    
    session = AuthenticatedSession(clients, auth_token, user_id, user_role)
    await session.setup()
    
    print(f"\n👤 Sessão autenticada como: {user_role} (ID: {user_id})")
    
    yield session
    
    await session.cleanup()


@pytest.fixture
def test_ids():
    """IDs padrão para testes (UUIDs válidos)"""
    return {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "clinic_id": "550e8400-e29b-41d4-a716-446655440001",
        "doctor_id": "550e8400-e29b-41d4-a716-446655440002",
        "patient_id": "550e8400-e29b-41d4-a716-446655440003",
        "appointment_id": "550e8400-e29b-41d4-a716-446655440004",
        "room_id": "550e8400-e29b-41d4-a716-446655440005",
        "rule_id": "550e8400-e29b-41d4-a716-446655440006",
        "notification_id": "550e8400-e29b-41d4-a716-446655440007",
    }


@pytest.fixture
def unique_suffix():
    """Gera um sufixo único para evitar conflitos entre testes"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


def pytest_configure(config):
    """Configuração de marcadores customizados"""
    config.addinivalue_line("markers", "agenda: testes para agendaService")
    config.addinivalue_line("markers", "users: testes para usersService")
    config.addinivalue_line("markers", "auth: testes para auth service")
    config.addinivalue_line("markers", "notification: testes para notificationService")
    config.addinivalue_line("markers", "analytic: testes para analyticService")
    config.addinivalue_line("markers", "health: testes de health check")
    config.addinivalue_line("markers", "integration: testes de integração entre services")
    config.addinivalue_line("markers", "flow: testes de fluxo completo end-to-end")
    config.addinivalue_line("markers", "slow: testes que levam mais tempo para executar")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def verify_services_healthy():
    """Verifica que todos os services estão saudáveis no início dos testes"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO SAÚDE DOS SERVICES")
    print("=" * 60)
    
    for service_name, url in SERVICE_URLS.items():
        try:
            async with ServiceClient(url, service_name) as client:
                pass  # health check é feito no __aenter__
        except ConnectionError as e:
            pytest.exit(f"❌ {str(e)}", 1)
    
    print("=" * 60)
    print("✅ TODOS OS SERVICES ESTÃO SAUDÁVEIS")
    print("=" * 60 + "\n")
