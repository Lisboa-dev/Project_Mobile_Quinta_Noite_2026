# 🧪 Testes de Endpoints - Guia Completo

Testes abrangentes de integração para todos os endpoints de todos os services do projeto Agendamento Médico.

**✨ NOVO**: Testes de fluxo completo (E2E) que simulam operações reais de usuários contra a API no ar.

## 📁 Estrutura dos Testes

```
tests/endpoint/
│
├── 🔧 CONFIGURAÇÃO E FIXTURES
│   ├── conftest.py                    (Clients HTTP, autenticação real, health checks)
│   └── mock_data.py                   (17 funções de dados mock)
│
├── 🧪 TESTES UNITÁRIOS POR SERVICE
│   ├── test_agenda_service.py         (42 endpoints testados)
│   ├── test_users_service.py          (23 endpoints testados)
│   ├── test_auth_service.py           (3 endpoints testados)
│   ├── test_notification_service.py   (22 endpoints testados)
│   └── test_analytic_service.py       (4 endpoints testados)
│
├── ✨ TESTES DE FLUXO COMPLETO (E2E)
│   └── test_complete_workflows.py     (6+ fluxos completos)
│
└── 📖 DOCUMENTAÇÃO
    ├── __init__.py                    (Docstring do package)
    ├── INDEX.md                       (Índice visual)
    ├── IMPLEMENTAÇÃO.md               (Resumo técnico)
    ├── verify.py                      (Script de verificação)
    └── README.md                      (Este arquivo)
```

## 🚀 Quick Start (30 segundos)

### 1. Services Rodando

```bash
# Verificar se já está rodando
docker compose ps

# Ou iniciar se necessário
docker compose up -d --build
```

### 2. Instalar Dependências (uma única vez)

```bash
pip install pytest pytest-asyncio httpx
```

### 3. Executar Testes

```bash
# ✅ Todos os testes (incluindo E2E)
pytest tests/endpoint/ -v

# ✨ Apenas fluxos completos (recomendado para começar)
pytest tests/endpoint/ -v -m flow

# 📊 Com saída detalhada (mostra cada requisição HTTP)
pytest tests/endpoint/ -vv -s

# 🔒 Apenas testes de autenticação
pytest tests/endpoint/ -v -m auth

# 🏥 Apenas health checks
pytest tests/endpoint/ -v -m health
```

## ✨ O Que Há de Novo: Testes E2E

### Fluxos Completos Testados

1. **Setup Inicial da Clínica** (`test_complete_clinic_setup_flow`)
   - Admin cria clínica
   - Admin cria 3 salas
   - Admin cria 2 médicos
   - Verifica métricas

2. **Agendamento de Consulta** (`test_patient_booking_complete_flow`)
   - Paciente lista médicos
   - Paciente consulta calendário
   - Paciente agenda consulta
   - Sistema gera notificações

3. **Jornada do Novo Paciente** (`test_new_user_complete_journey`)
   - Novo paciente se registra
   - Novo paciente faz login
   - Novo paciente visualiza médicos
   - Novo paciente consulta agenda

4. **Integração Entre Services** (`test_event_flow_across_services`)
   - Evento criado em um service
   - Analytics captura evento
   - Notificações são geradas
   - Métricas atualizadas

5. **Simulação de Cliente Frontend** (`test_frontend_client_simulation`)
   - Simula carregamento de dashboard
   - Aplica filtros e buscas
   - Executa CRUD operations
   - Carrega dados paralelos

6. **Health Check Completo** (`test_all_services_health_check`)
   - Verifica saúde de todos os 5 services
   - Garante que APIs estão responsivas

### Características dos Testes E2E

✅ **Autenticação Real**: Login e tokens JWT genuínos  
✅ **Fluxos Completos**: Múltiplas requisições em sequência  
✅ **Estado Rastreado**: Registra entidades criadas para cleanup  
✅ **Integração Multi-Service**: Testa chamadas entre services  
✅ **Logging Detalhado**: Mostra cada passo do fluxo  
✅ **Erro Handling**: Valida comportamento em cenários problemáticos  

## 📊 Coverage de Endpoints

| Service | Endpoints | Cobertura | Status |
|---------|-----------|-----------|--------|
| agendaService | 42 | 100% | ✅ |
| usersService | 23 | 100% | ✅ |
| auth | 3 | 100% | ✅ |
| notificationService | 22 | 100% | ✅ |
| analyticService | 4 | 100% | ✅ |
| **Fluxos E2E** | **6+** | 100% | ✅ |
| **TOTAL** | **94+** | **100%** | ✅ |

## 🏗️ Arquitetura dos Testes

### ServiceClient (conftest.py)

```python
async with ServiceClient(base_url, service_name) as client:
    client.set_auth_token(token, user_id, user_role)
    response = await client.get("/path")
```

**Recursos**:
- ✅ Health checks com retry
- ✅ Autenticação com JWT
- ✅ Retry automático em falhas
- ✅ Logging de requisições HTTP
- ✅ Timeout configurável

### AuthenticatedSession (conftest.py)

```python
async def authenticated_session(auth_token, ...):
    session = AuthenticatedSession(clients, token, user_id, role)
    await session.setup()  # Configura autenticação
    session.track_entity("type", "id")  # Rastreia criações
```

**Recursos**:
- ✅ Gerencia autenticação de múltiplos clients
- ✅ Rastreia entidades para cleanup
- ✅ Simula sessão de usuário real

## 🔐 Autenticação Real

Os testes usam:
- **Credenciais Reais**: `admin@clinica.local` / `Admin123!` (seeded no startup)
- **JWT Token**: Extraído do response de login
- **User Context**: Informações do usuário rastreadas durante o fluxo
- **Cleanup Automático**: Entidades criadas durante testes são registradas

Exemplo:
```python
async def test_flow(authenticated_session):
    # authenticated_session já tem token, user_id, user_role
    agenda = authenticated_session.clients["agenda"]
    
    response = await agenda.post("/agenda/clinics/", json=data)
    clinic_id = response.json().get("id")
    
    # Rastreia para cleanup posterior
    authenticated_session.track_entity("clinics", clinic_id)
```

## 🎯 Executando Diferentes Tipos de Testes

### Health Checks (Validação Rápida)

```bash
# Verifica se todos os services estão saudáveis
pytest tests/endpoint/ -v -m health -s
```

Output esperado:
```
✓ agendaService health check: OK
✓ usersService health check: OK
✓ authService health check: OK
✓ notificationService health check: OK
✓ analyticService health check: OK
```

### Fluxos E2E (Testes de Negócio)

```bash
# Executa fluxos completos realistas
pytest tests/endpoint/ -v -m flow -s

# Apenas fluxos lentos (mais operações)
pytest tests/endpoint/ -v -m "flow and slow" -s
```

Output esperado:
```
📋 FLUXO: Setup Inicial da Clínica
1️⃣ Criando clínica...
   ✅ Clínica criada: uuid-123
2️⃣ Criando salas...
   ✅ Sala 1 criada: uuid-456
   ✅ Sala 2 criada: uuid-789
   ✅ Sala 3 criada: uuid-abc
3️⃣ Listando salas...
   ✅ 3 salas encontradas
... (continua)
✅ FLUXO CONCLUÍDO COM SUCESSO
```

### Integration Tests

```bash
# Testes que abrangem múltiplos services
pytest tests/endpoint/ -v -m integration -s
```

### Por Service Específico

```bash
pytest tests/endpoint/ -v -m agenda        # agendaService
pytest tests/endpoint/ -v -m users         # usersService
pytest tests/endpoint/ -v -m auth          # auth service
pytest tests/endpoint/ -v -m notification  # notificationService
pytest tests/endpoint/ -v -m analytic      # analyticService
```

## 🔍 Debugging Detalhado

### Ver todas as requisições HTTP

```bash
pytest tests/endpoint/test_complete_workflows.py -vv -s
```

Mostra cada requisição:
```
→ POST /agenda/clinics/ → 201
→ GET /agenda/rooms/ → 200
→ POST /medics/ → 201
...
```

### Executar teste específico

```bash
pytest tests/endpoint/test_complete_workflows.py::TestAdminInitialSetup::test_complete_clinic_setup_flow -vv -s
```

### Com traceback completo

```bash
pytest tests/endpoint/ -v --tb=long -s
```

### Medir duração de testes

```bash
pytest tests/endpoint/ -v --durations=10
```

## 🛠️ Configuração

### Variáveis de Ambiente (Opcional)

Se os services não estão em localhost:8000-8004:

```bash
export AGENDA_SERVICE_URL=http://192.168.1.100:8000
export USERS_SERVICE_URL=http://192.168.1.100:8004
export AUTH_SERVICE_URL=http://192.168.1.100:8002
export NOTIFICATION_SERVICE_URL=http://192.168.1.100:8003
export ANALYTIC_SERVICE_URL=http://192.168.1.100:8001

pytest tests/endpoint/ -v
```

### Timeouts

Ajustar em `conftest.py`:

```python
TIMEOUT = 60.0  # Segundos
MAX_RETRIES = 10  # Tentativas de conexão
RETRY_DELAY = 3  # Segundos entre tentativas
```

## 📝 Exemplo: Criando Novo Fluxo

```python
@pytest.mark.flow
class TestMyCustomFlow:
    """Descrição do fluxo"""
    
    async def test_my_flow(self, authenticated_session):
        """Fluxo custom"""
        print("\n" + "=" * 60)
        print("📋 FLUXO: Meu Fluxo Custom")
        print("=" * 60)
        
        # Acessa clients autenticados
        agenda = authenticated_session.clients["agenda"]
        users = authenticated_session.clients["users"]
        
        # Step 1
        print("\n1️⃣ Primeiro passo...")
        response = await agenda.get("/agenda/clinics/")
        assert response.status_code == 200
        print(f"   ✅ Clínicas carregadas")
        
        # Step 2
        print("\n2️⃣ Segundo passo...")
        data = mock_data.clinic_data()
        response = await agenda.post("/agenda/clinics/", json=data)
        clinic_id = response.json().get("id")
        authenticated_session.track_entity("clinics", clinic_id)
        print(f"   ✅ Clínica criada: {clinic_id}")
        
        print("\n✅ FLUXO CONCLUÍDO\n")
```

## ⚠️ Troubleshooting

### Services não estão respondendo

```bash
# Verificar status
docker compose ps

# Ver logs
docker compose logs

# Reiniciar
docker compose up -d --build
```

### Timeout nos testes

Services podem estar lentos:
```bash
# Aumentar timeout em conftest.py
RETRY_DELAY = 5  # Aumentar delay entre tentativas
```

### Erro de autenticação

Verificar se admin padrão existe:
```bash
docker compose exec users-service python -c "from src.server import seed_users; seed_users()"
```

### Testes não encontram services

```bash
# Verificar URLs
echo $AGENDA_SERVICE_URL
echo $USERS_SERVICE_URL

# Acessar diretamente
curl http://localhost:8000/health
curl http://localhost:8004/health
```

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      docker:
        image: docker:latest
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - run: docker compose up -d --build
      - run: sleep 10  # Aguarda services iniciarem
      - run: pip install pytest pytest-asyncio httpx
      - run: pytest tests/endpoint/ -v --junit-xml=results.xml
      
      - uses: actions/upload-artifact@v2
        if: always()
        with:
          name: test-results
          path: results.xml
```

## 📚 Referência Rápida

| Comando | Descrição |
|---------|-----------|
| `pytest tests/endpoint/ -v` | Todos os testes |
| `pytest tests/endpoint/ -v -m flow` | Apenas fluxos E2E |
| `pytest tests/endpoint/ -v -m health` | Health checks |
| `pytest tests/endpoint/ -vv -s` | Com saída detalhada |
| `pytest tests/endpoint/ --collect-only` | Lista testes sem executar |
| `pytest tests/endpoint/ -k "clinic"` | Testes com "clinic" no nome |

## 🎓 Aprendendo

1. **Comece com health checks**: `pytest tests/endpoint/ -v -m health`
2. **Depois fluxos simples**: `pytest tests/endpoint/ -v -m flow --co` (apenas listar)
3. **Execute um fluxo**: `pytest tests/endpoint/ -v -m flow -s` (com output)
4. **Analise os logs**: Veja como os testes fazem requisições reais
5. **Crie seu fluxo**: Copie a estrutura de `test_complete_workflows.py`

## 📊 Resultados Esperados

Quando tudo funciona:
```
tests/endpoint/test_auth_service.py::TestAuthLoginEndpoints::test_login_success PASSED
tests/endpoint/test_complete_workflows.py::TestAdminInitialSetup::test_complete_clinic_setup_flow PASSED
...

======================== 94 passed in 45.23s ========================
```

## 🤝 Contribuindo

Para adicionar novos testes E2E:

1. Crie uma classe em `test_complete_workflows.py`
2. Use `@pytest.mark.flow` e marcadores adicionais
3. Documente o fluxo com prints informativos
4. Rastreie entidades: `authenticated_session.track_entity("type", "id")`
5. Execute: `pytest tests/endpoint/ -v -m flow -s`

## 📞 Suporte

- Documentação detalhada: [INDEX.md](INDEX.md)
- Implementação: [IMPLEMENTAÇÃO.md](IMPLEMENTAÇÃO.md)
- Verificação: `python tests/endpoint/verify.py`

---

**Última atualização**: 2026-06-11  
**Endpoints testados**: 94+  
**Tempo de execução**: ~1-2 minutos (todos)  
**Dependências**: pytest, pytest-asyncio, httpx
