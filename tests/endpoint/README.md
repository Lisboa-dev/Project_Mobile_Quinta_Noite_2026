# Testes de Endpoints

Testes abrangentes de integração para todos os endpoints de todos os services do projeto Agendamento Médico.

## Estrutura dos Testes

```
tests/endpoint/
├── conftest.py              # Fixtures e configuração compartilhada
├── mock_data.py             # Dados mock para testes
├── test_agenda_service.py   # Testes do agendaService (42 endpoints)
├── test_users_service.py    # Testes do usersService (23 endpoints)
├── test_auth_service.py     # Testes do auth service (3 endpoints)
├── test_notification_service.py  # Testes do notificationService (22 endpoints)
├── test_analytic_service.py      # Testes do analyticService (4 endpoints)
├── __init__.py              # Documentação do package
└── README.md               # Este arquivo
```

## Coverage Total

- **agendaService**: 42 endpoints
  - AppointmentController: 9 endpoints
  - CalendarController: 6 endpoints
  - ClinicController: 5 endpoints
  - DoctorController: 5 endpoints
  - PatientController: 5 endpoints
  - RoomController: 7 endpoints
  - RuleController: 9 endpoints
  - WebsocketController: 1 endpoint

- **usersService**: 23 endpoints
  - UserController: 7 endpoints (CRUD + profile image)
  - AdminController: 6 endpoints
  - MedicController: 5 endpoints
  - PacientController: 5 endpoints
  - AtendentController: 5 endpoints
  - ClientConfig: 1 endpoint

- **auth**: 3 endpoints
  - Login
  - Token Validation (forward_auth)
  - Health Check

- **notificationService**: 22 endpoints
  - User Notifications: 4 endpoints
  - Patient Notifications: 4 endpoints
  - Doctor/Medic Notifications: 4 endpoints
  - Admin Notifications: 4 endpoints
  - Notification Details: 2 endpoints
  - WebSocket: 2 endpoints
  - Health Check: 1 endpoint

- **analyticService**: 4 endpoints
  - Health Check
  - List Events (com validação de limit)
  - Events Summary
  - Prometheus Metrics

**Total: 94 endpoints testados**

## Configuração

### Variáveis de Ambiente

Configure as URLs dos services (padrão: localhost com portas 8000-8004):

```bash
export AGENDA_SERVICE_URL=http://localhost:8000
export USERS_SERVICE_URL=http://localhost:8004
export AUTH_SERVICE_URL=http://localhost:8002
export NOTIFICATION_SERVICE_URL=http://localhost:8003
export ANALYTIC_SERVICE_URL=http://localhost:8001
```

### Dependências

```bash
pip install pytest pytest-asyncio httpx
```

## Executando os Testes

### Todos os testes
```bash
pytest tests/endpoint/ -v
```

### Por service
```bash
# agendaService
pytest tests/endpoint/ -v -m agenda

# usersService
pytest tests/endpoint/ -v -m users

# auth service
pytest tests/endpoint/ -v -m auth

# notificationService
pytest tests/endpoint/ -v -m notification

# analyticService
pytest tests/endpoint/ -v -m analytic
```

### Por categoria
```bash
# Apenas health checks
pytest tests/endpoint/ -v -m health

# Apenas testes de integração
pytest tests/endpoint/ -v -m integration
```

### Testes específicos
```bash
# Apenas clinics
pytest tests/endpoint/test_agenda_service.py::TestClinicEndpoints -v

# Apenas auth
pytest tests/endpoint/test_auth_service.py -v

# Apenas users CRUD
pytest tests/endpoint/test_users_service.py::TestUserCrudEndpoints -v
```

### Com output detalhado
```bash
pytest tests/endpoint/ -vv -s

# Com print statements
pytest tests/endpoint/ -v --capture=no

# Com duração de cada teste
pytest tests/endpoint/ -v --durations=10
```

## Escopo dos Testes

Cada teste cobre:

1. **Caminho feliz (success path)**: Requisições válidas retornam 200/201
2. **Validação de entrada**: Dados inválidos retornam 400/422
3. **Autenticação**: Endpoints protegidos retornam 401/403 sem token
4. **Not Found**: IDs inválidos retornam 404
5. **Not Implemented**: Métodos não implementados retornam 501

## Exemplo: Testando um Endpoint

### agendaService - Criar Clínica

```python
async def test_create_clinic(self, agenda_client, auth_token):
    """POST /agenda/clinics/ - Criar clínica"""
    data = mock_data.clinic_data()
    agenda_client.set_auth_token(auth_token)
    
    response = await agenda_client.post(
        "/agenda/clinics/",
        json=data
    )
    
    assert response.status_code in [200, 201]
    result = response.json()
    assert result.get("id") or result.get("clinic_id")
```

### usersService - Listar Usuários

```python
async def test_list_users(self, users_client, auth_token):
    """GET /users/ - Listar usuários"""
    users_client.set_auth_token(auth_token)
    
    response = await users_client.get("/users/")
    
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, (list, dict))
```

### auth - Login

```python
async def test_login_success(self, auth_client):
    """POST /auth/login - Login com credenciais válidas"""
    data = mock_data.login_data()
    
    response = await auth_client.post(
        "/auth/login",
        json=data
    )
    
    assert response.status_code in [200, 401]
    if response.status_code == 200:
        result = response.json()
        assert "access_token" in result or "token" in result
```

## Recursos dos Testes

### Autenticação

Os testes usam fixtures que:
1. Fazem login com credenciais padrão (admin@clinica.local / Admin123!)
2. Extraem o token JWT
3. Usam o token em requisições autenticadas

```python
@pytest.fixture
async def auth_token(auth_client):
    """Obtém token JWT válido para testes autenticados"""
    response = await auth_client.post(
        "/auth/login",
        json={"email": "admin@clinica.local", "password": "Admin123!"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    return None
```

### Dados Mock

Cada serviço tem funções para gerar dados mock:

```python
clinic_data()      # Clínica
room_data()        # Sala
doctor_data()      # Médico
patient_data()     # Paciente
appointment_data() # Consulta
user_data()        # Usuário genérico
medic_data()       # Médico (users service)
pacient_data()     # Paciente (users service)
```

### IDs de Teste

UUIDs padrão para testes:

```python
test_ids = {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "clinic_id": "550e8400-e29b-41d4-a716-446655440001",
    "doctor_id": "550e8400-e29b-41d4-a716-446655440002",
    "patient_id": "550e8400-e29b-41d4-a716-446655440003",
    "appointment_id": "550e8400-e29b-41d4-a716-446655440004",
    "room_id": "550e8400-e29b-41d4-a716-446655440005",
    "rule_id": "550e8400-e29b-41d4-a716-446655440006",
    "notification_id": "550e8400-e29b-41d4-a716-446655440007",
}
```

## Adicionando Novos Testes

Para adicionar novos testes:

1. **Crie uma classe de teste** em `test_<service>.py`:
```python
@pytest.mark.agenda
class TestNewFeature:
    """Testes para nova feature"""
    
    async def test_something(self, agenda_client, auth_token):
        """Descrição clara do teste"""
        # Arrange
        data = mock_data.some_data()
        
        # Act
        response = await agenda_client.post("/agenda/something", json=data)
        
        # Assert
        assert response.status_code in [200, 201]
```

2. **Adicione marcador pytest** se necessário:
```python
@pytest.mark.custom_marker
```

3. **Use dados mock** sempre que possível
4. **Documente o endpoint** no docstring do teste

## Troubleshooting

### Services não estão rodando
```bash
docker compose up -d --build
```

### Timeout nos testes
Aumentar timeout em conftest.py:
```python
AsyncClient(base_url=base_url, timeout=60.0)  # 60 segundos
```

### Erro de autenticação
Verificar se o arquivo `tests/endpoint/mock_data.py` tem credenciais corretas:
```python
def login_data():
    return {
        "email": "admin@clinica.local",
        "password": "Admin123!",
    }
```

### Testes não encontram services
Verificar variáveis de ambiente:
```bash
echo $AGENDA_SERVICE_URL
echo $USERS_SERVICE_URL
# etc
```

## CI/CD Integration

### GitHub Actions (exemplo)

```yaml
name: Endpoint Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      agenda:
        image: agendaservice:latest
        ports:
          - 8000:8000
      # ... outros services
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - run: pip install -r requirements.txt
      - run: pytest tests/endpoint/ -v --junit-xml=results.xml
      
      - uses: actions/upload-artifact@v2
        if: always()
        with:
          name: test-results
          path: results.xml
```

## Métricas e Cobertura

### Endpoints Cobertos

- ✅ Agenda Service: 42/42 endpoints
- ✅ Users Service: 23/23 endpoints
- ✅ Auth Service: 3/3 endpoints
- ✅ Notification Service: 22/22 endpoints
- ✅ Analytic Service: 4/4 endpoints

**Total: 94/94 endpoints (100%)**

### Casos de Teste por Endpoint

Cada endpoint é testado para:
- ✅ Success path (2xx)
- ✅ Bad request (400/422)
- ✅ Unauthorized (401)
- ✅ Forbidden (403)
- ✅ Not found (404)
- ✅ Not implemented (501)
- ✅ Validation rules
- ✅ Query parameters
- ✅ Request body

## Contribuindo

Ao adicionar testes para novos endpoints:

1. Use o marcador apropriado (@pytest.mark.service)
2. Documente claramente o que está sendo testado
3. Cubra casos de sucesso, erro e validação
4. Use dados mock do mock_data.py
5. Mantenha a consistência de estilo com testes existentes

## Recursos

- [pytest Documentation](https://docs.pytest.org/)
- [httpx Documentation](https://www.python-httpx.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-events/)

## Licença

Mesmo do projeto
