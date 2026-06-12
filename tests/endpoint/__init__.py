"""
Testes de integração de endpoints para todos os services.

Este pacote contém testes que validam todos os endpoints de cada service:
- agendaService: Clinics, Rooms, Appointments, Calendars, Rules, Doctors, Patients
- usersService: User CRUD, Admins, Medics, Pacients, Atendents, Config
- auth: Login, Token Validation, Health
- notificationService: User/Patient/Doctor/Admin notifications, WebSockets
- analyticService: Events, Metrics, Health

Estrutura:
- conftest.py: Fixtures e configuração compartilhada
- mock_data.py: Dados de teste para cada serviço
- test_*.py: Testes para cada serviço

Para rodar os testes:
    pytest tests/endpoint/ -v
    
Para rodar testes de um serviço específico:
    pytest tests/endpoint/ -v -m agenda
    pytest tests/endpoint/ -v -m users
    pytest tests/endpoint/ -v -m auth
    pytest tests/endpoint/ -v -m notification
    pytest tests/endpoint/ -v -m analytic

Para rodar apenas health checks:
    pytest tests/endpoint/ -v -m health

Para rodar testes de integração:
    pytest tests/endpoint/ -v -m integration

Variáveis de ambiente (opcional):
    AGENDA_SERVICE_URL: URL do agendaService (padrão: http://localhost:8000)
    ANALYTIC_SERVICE_URL: URL do analyticService (padrão: http://localhost:8001)
    AUTH_SERVICE_URL: URL do auth service (padrão: http://localhost:8002)
    NOTIFICATION_SERVICE_URL: URL do notificationService (padrão: http://localhost:8003)
    USERS_SERVICE_URL: URL do usersService (padrão: http://localhost:8004)
"""
