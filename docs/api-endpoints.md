# API endpoints dos servicos

Este guia mostra como chamar cada servico, quais parametros enviar e o que esperar de retorno. A documentacao interativa tambem fica disponivel em `/docs` quando o servico estiver rodando.

## Base URLs

| Servico | Porta direta | Docs |
| --- | --- | --- |
| Auth | `http://localhost:8000` | `http://localhost:8000/docs` |
| Agenda | `http://localhost:8001` | `http://localhost:8001/docs` |
| Users | `http://localhost:8002` | `http://localhost:8002/docs` |
| Notification | `http://localhost:8003` | `http://localhost:8003/docs` |
| Analytics | `http://localhost:8005` | `http://localhost:8005/docs` |

Via Traefik, use `http://localhost` com os prefixos `/auth`, `/agenda`, `/users`, `/notification` e `/analytics`.

## Padroes gerais

Headers recomendados para JSON:

```http
Content-Type: application/json
Accept: application/json
```

Quando a rota estiver protegida pelo gateway, envie:

```http
Authorization: Bearer <token>
```

Respostas comuns:

| Status | Significado |
| --- | --- |
| `200` | Operacao executada com sucesso. |
| `201` | Recurso criado. |
| `204` | Recurso removido; resposta sem body. |
| `400` | Requisicao invalida. |
| `401` | Sem autenticacao. |
| `403` | Autenticado, mas sem permissao. |
| `404` | Recurso nao encontrado. |
| `409` | Conflito, geralmente email/usuario ja existente. |
| `422` | Erro de validacao de parametro ou body. |
| `500` | Erro interno. |

Erro de validacao FastAPI:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

## Auth Service

Base URL: `http://localhost:8000`

| Metodo | Endpoint | Uso | Entrada | Retorno esperado |
| --- | --- | --- | --- | --- |
| `GET` | `/health` | Healthcheck do servico. | Nenhuma. | `{"status":"ok","service":"..."}` |
| `POST` | `/auth/login` | Autentica usuario e retorna token. | JSON com credenciais. | JSON com tokens/dados de login, ou `401`. |
| `GET` | `/auth/validate` | Validacao usada pelo Traefik/auth middleware. | Header `Authorization: Bearer <token>`. | `200` com headers `X-User-Id` e `X-User-Role`; `401`, `403` ou `500`. |

### Body esperado para login

O endpoint `POST /auth/login` espera `Content-Type: application/json`.

Campos aceitos:

| Campo | Tipo | Obrigatorio | Observacao |
| --- | --- | --- | --- |
| `password` | string | Sim | Senha do usuario. |
| `email` | string | Condicional | Informe `email` ou `name`. |
| `name` | string | Condicional | Informe `name` ou `email`. |

Body usando email:

```json
{
  "email": "admin@clinica.local",
  "password": "Admin123!"
}
```

Body usando nome de usuario:

```json
{
  "name": "admin",
  "password": "Admin123!"
}
```

Se `password` nao for enviado, ou se nenhum identificador (`email` ou `name`) for enviado, o servico retorna `400`.

Resposta esperada em caso de sucesso:

```json
{
  "user_id": "auth-user-1",
  "tokens": {
    "access_token": "<jwt>",
    "refresh_token": "<jwt>",
    "token_type": "Bearer"
  }
}
```

Resposta esperada em credenciais invalidas:

```json
{
  "error": "invalid credentials"
}
```

Exemplo:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@clinica.local\",\"password\":\"Admin123!\"}"
```

### Header esperado para validacao

O endpoint `GET /auth/validate` nao recebe body. Ele espera o token no header:

```http
Authorization: Bearer <access_token>
```

Quando o token e valido, retorna `200` sem body e adiciona headers para o Traefik encaminhar aos servicos:

```http
X-User-Id: auth-user-1
X-User-Role: admin
```

## Users Service

Base URL: `http://localhost:8002`

### Schemas principais

`UserCreateRequest`:

```json
{
  "userName": "joao",
  "email": "joao@email.com",
  "name": "Joao Silva",
  "password": "Senha123!",
  "cargo": "PACIENTE"
}
```

`cargo` aceita: `ADMIN`, `MEDICO`, `ATENDENTE`, `PACIENTE`, `GERENTE`, `SUPERVISOR`.

`MedicCreateRequest`:

```json
{
  "userName": "dra_ana",
  "email": "ana@clinica.local",
  "name": "Dra Ana",
  "password": "Medico123!",
  "crm": "CRM-12345"
}
```

`AtendenteCreateRequest` e `PacientCreateRequest`:

```json
{
  "userName": "maria",
  "email": "maria@email.com",
  "name": "Maria Souza",
  "password": "Senha123!",
  "cpf": "12345678901"
}
```

`UserUpdateRequest` aceita campos opcionais:

```json
{
  "userName": "novo_nome",
  "email": "novo@email.com",
  "name": "Novo Nome",
  "password": "NovaSenha123!",
  "cargo": "ATENDENTE",
  "crm": "CRM-999",
  "cpf": "12345678901"
}
```

`UserResponse`:

```json
{
  "id": 1,
  "userName": "joao",
  "email": "joao@email.com",
  "name": "Joao Silva",
  "cargo": "PACIENTE",
  "profileImageUrl": null
}
```

`UseCaseResponse`:

```json
{
  "success": true,
  "use_case": "CreateMedicUseCase",
  "action": "created",
  "resource": "user",
  "resource_id": "1",
  "triggered_by_id": null,
  "event_name": "users.doctor.created",
  "message": null,
  "data": {}
}
```

### Endpoints de usuarios

| Metodo | Endpoint | Uso | Entrada | Retorno esperado |
| --- | --- | --- | --- | --- |
| `GET` | `/health` | Healthcheck. | Nenhuma. | `{"status":"ok"}` |
| `GET` | `/users/` | Lista usuarios. | Nenhuma. | `UserResponse[]` |
| `POST` | `/users/` | Cria usuario generico. | `UserCreateRequest`. | `201 UserResponse`; `409` em conflito. |
| `GET` | `/users/{user_id}` | Detalha usuario. | Path `user_id` inteiro. | `UserResponse`; `404`. |
| `PUT` | `/users/{user_id}` | Atualiza usuario. | Path `user_id`; `UserUpdateRequest`. | `UserResponse`; `404`. |
| `DELETE` | `/users/{user_id}` | Remove usuario. | Path `user_id`. | `204`; `404`. |
| `POST` | `/users/{user_id}/profile-image` | Envia imagem de perfil. | `multipart/form-data`, campo `file`. | `UserResponse`; `400`; `404`. |
| `DELETE` | `/users/{user_id}/profile-image` | Remove imagem de perfil. | Path `user_id`. | `UserResponse`; `404`. |
| `GET` | `/user/` | Lookup usado pelo Auth. | Query `email` ou `name`. | Lista com usuario encontrado ou `[]`. |
| `GET` | `/config/client` | Configuracoes para frontend. | Nenhuma. | Dados de limite/tipos de imagem. |

Exemplo upload:

```bash
curl -X POST http://localhost:8002/users/1/profile-image \
  -F "file=@avatar.png"
```

### Endpoints por papel

| Metodo | Endpoint | Uso | Body |
| --- | --- | --- | --- |
| `GET` | `/admins/` | Lista admins. | Nenhum. |
| `GET` | `/admins/{user_id}` | Detalha admin. | Nenhum. |
| `POST` | `/admins/{user_id}/promote` | Promove usuario para admin. | Nenhum. |
| `POST` | `/admins/doctors` | Admin cria medico. | `MedicCreateRequest`. |
| `POST` | `/admins/{user_id}/depreciate` | Rebaixa admin. | Nenhum. |
| `DELETE` | `/admins/{user_id}` | Remove admin. | Nenhum. |
| `GET` | `/atendents/` | Lista atendentes. | Nenhum. |
| `POST` | `/atendents/` | Cria atendente. | `AtendenteCreateRequest`. |
| `GET` | `/atendents/{user_id}` | Detalha atendente. | Nenhum. |
| `PUT` | `/atendents/{user_id}` | Atualiza atendente. | `UserUpdateRequest`; pode retornar `501`. |
| `DELETE` | `/atendents/{user_id}` | Remove atendente. | Nenhum. |
| `GET` | `/medics/` | Lista medicos. | Nenhum. |
| `POST` | `/medics/` | Cria medico. | `MedicCreateRequest`. |
| `GET` | `/medics/{user_id}` | Detalha medico. | Nenhum. |
| `PUT` | `/medics/{user_id}` | Atualiza medico. | `UserUpdateRequest`; pode retornar `501`. |
| `DELETE` | `/medics/{user_id}` | Remove medico. | Nenhum. |
| `GET` | `/pacients/` | Lista pacientes. | Nenhum. |
| `POST` | `/pacients/` | Cria paciente. | `PacientCreateRequest`. |
| `GET` | `/pacients/{user_id}` | Detalha paciente. | Nenhum. |
| `PUT` | `/pacients/{user_id}` | Atualiza paciente. | `UserUpdateRequest`; pode retornar `501`. |
| `DELETE` | `/pacients/{user_id}` | Remove paciente. | Nenhum. |

## Agenda Service

Base URL: `http://localhost:8001`

Todas as rotas do servico usam o prefixo `/agenda`.

No OpenAPI publico do Agenda aparecem apenas `appointments` e `rooms`. Doctors e patients sao espelhados automaticamente por eventos do Users Service; calendar, clinic, rules e endpoints de infra sao rotas operacionais/internas e ficam fora do schema publico.

Campos comuns:

| Campo | Uso |
| --- | --- |
| `triggered_by_id` | Opcional. Id de quem disparou a acao, usado em eventos/auditoria. |
| `limit` | Opcional em listagens. Limita quantidade. |
| `offset` | Opcional em listagens. Padrao `0`. |

### Appointments

`CreateAppointmentRequest`:

```json
{
  "scheduler_id": "user-1",
  "date": "2026-06-10",
  "weekday": "wednesday",
  "doctor": "doctor-1",
  "patient": "patient-1",
  "time": "09:00",
  "type": "consulta",
  "room": "room-1",
  "triggered_by_id": "admin-1"
}
```

| Metodo | Endpoint | Entrada | Retorno esperado |
| --- | --- | --- | --- |
| `POST` | `/agenda/appointments/` | Body `CreateAppointmentRequest`. | `201` com objeto/resultado criado. |
| `GET` | `/agenda/appointments/` | Query `limit`, `offset`. | Lista de agendamentos. |
| `GET` | `/agenda/appointments/{appointment_id}` | Path `appointment_id`. | Agendamento ou `404`. |
| `PUT` | `/agenda/appointments/{appointment_id}` | Body com `triggered_by_id` opcional. | Resultado da atualizacao. |
| `DELETE` | `/agenda/appointments/{appointment_id}` | Path `appointment_id`. | `204`. |

### Calendars

`CreateCalendarRequest`:

```json
{
  "mes": 6,
  "ano": 2026,
  "triggered_by_id": "admin-1"
}
```

Gera e persiste todos os dias do mes informado em `mes`, respeitando anos bissextos. Exemplo: `mes=2`, `ano=2024` gera 29 dias; `mes=2`, `ano=2023` gera 28 dias.

`UpdateDayRequest`:

```json
{
  "data": {
    "available": true,
    "notes": "Atendimento normal"
  },
  "triggered_by_id": "admin-1"
}
```

| Metodo | Endpoint | Entrada | Retorno esperado |
| --- | --- | --- | --- |
| `POST` | `/agenda/calendars/` | Body `CreateCalendarRequest`. | `201`. |
| `GET` | `/agenda/calendars/days` | Query `year`, `month`, `limit`, `offset`. | Lista de dias. |
| `GET` | `/agenda/calendars/days/{day_id}` | Path `day_id`. | Dia/calendario. |
| `PATCH` | `/agenda/calendars/days/{day_id}` | Body `UpdateDayRequest`. | Dia atualizado. |
| `DELETE` | `/agenda/calendars/{ano}` | Path `ano` inteiro. | `204`. |

### Clinics e rooms

Bodies:

```json
// POST /agenda/clinics/
{
  "name": "Clinica Central",
  "rules": [],
  "triggered_by_id": "admin-1"
}
```

```json
// POST /agenda/rooms/
{
  "name": "Sala 01",
  "triggered_by_id": "admin-1"
}
```

| Recurso | Criar | Listar | Detalhar | Atualizar | Remover |
| --- | --- | --- | --- | --- | --- |
| Clinics | `POST /agenda/clinics/` | `GET /agenda/clinics/?limit=50&offset=0` | `GET /agenda/clinics/{clinic_id}` | `PUT /agenda/clinics/{clinic_id}` | `DELETE /agenda/clinics/{clinic_id}` |
| Rooms | `POST /agenda/rooms/` | `GET /agenda/rooms/?limit=50&offset=0` | `GET /agenda/rooms/{room_id}` | `PUT /agenda/rooms/{room_id}` | `DELETE /agenda/rooms/{room_id}` |

Todos os endpoints de rooms exigem usuario admin via header encaminhado pelo gateway:

```http
X-User-Role: admin
```

Doctors e patients nao sao criados, listados ou consultados diretamente pela API publica do Agenda. Eles sao espelhados automaticamente a partir dos eventos do Users Service descritos em `Infra e websocket`.

Updates aceitam campos opcionais:

```json
// Clinic
{ "name": "Novo nome", "rules": [], "triggered_by_id": "admin-1" }
```

```json
// Room
{ "name": "Sala 02", "disponibility": true, "rules": [], "triggered_by_id": "admin-1" }
```

### Rules

`rangeTime` aceita objeto ou estrutura compativel com o dominio. Use preferencialmente:

```json
{
  "start": "08:00",
  "end": "12:00"
}
```

| Metodo | Endpoint | Entrada | Retorno esperado |
| --- | --- | --- | --- |
| `GET` | `/agenda/rules/` | Query `limit`, `offset`. | Lista de regras. |
| `GET` | `/agenda/rules/{rule_id}` | Path `rule_id`. | Regra. |
| `DELETE` | `/agenda/rules/{rule_id}` | Path `rule_id`. | `204`. |
| `POST` | `/agenda/rules/block` | Body `CreateBlockRuleRequest`. | `201`. |
| `POST` | `/agenda/rules/generic` | Body `CreateGenericRuleRequest`. | `201`. |
| `POST` | `/agenda/rules/specific` | Body `CreateSpecificRuleRequest`. | `201`. |
| `POST` | `/agenda/rules/specific-day` | Body `CreateSpecificDayRuleRequest`. | `201`. |
| `POST` | `/agenda/rules/week` | Body `CreateWeekRuleRequest`. | `201`. |

Exemplos:

```json
// block
{
  "date": "2026-06-10",
  "weekday": null,
  "description": "Feriado",
  "target": null,
  "targetType": "clinic",
  "nome": "Bloqueio feriado"
}
```

```json
// generic
{
  "ruleEffect": "allow",
  "targetType": "doctor",
  "rangeTime": { "start": "08:00", "end": "12:00" },
  "description": "Atendimento pela manha",
  "nome": "Regra manha"
}
```

```json
// specific
{
  "ruleEffect": "deny",
  "target": "doctor-1",
  "rangeTime": { "start": "12:00", "end": "13:00" },
  "description": "Almoco",
  "nome": "Intervalo"
}
```

```json
// specific-day
{
  "ruleEffect": "allow",
  "rangeTime": { "start": "14:00", "end": "18:00" },
  "description": "Horario extra",
  "date": "2026-06-10",
  "target": "doctor-1",
  "targetType": "doctor"
}
```

```json
// week
{
  "ruleEffect": "allow",
  "rangeTime": { "start": "08:00", "end": "17:00" },
  "description": "Horario semanal",
  "weekday": 1,
  "target": "doctor-1",
  "targetType": "doctor"
}
```

### Infra e websocket

| Metodo | Endpoint | Entrada | Retorno esperado |
| --- | --- | --- | --- |
| `GET` | `/agenda/infra/health` | Nenhuma. | Health do servico. |
| `GET` | `/agenda/infra/ready` | Nenhuma. | Readiness. |
| `POST` | `/agenda/infra/events/users/doctor-created` | `InfraEventRequest`. | Resultado do handler. |
| `POST` | `/agenda/infra/events/users/patient-created` | `InfraEventRequest`. | Resultado do handler. |
| `POST` | `/agenda/infra/events/users/doctor-deleted` | `InfraEventRequest`. | Resultado do handler. |
| `POST` | `/agenda/infra/events/users/patient-deleted` | `InfraEventRequest`. | Resultado do handler. |
| `WS` | `/agenda/ws` | WebSocket. | Eventos publicados pelo event bus do Agenda em tempo real, como `agenda.calendar.created`, `agenda.appointment.created` e demais eventos `agenda.*`. |

`InfraEventRequest`:

```json
{
  "event": "MedicCreatedEvent",
  "data": {
    "id": "medic-1",
    "userName": "dra.ana",
    "name": "Dra Ana",
    "email": "ana@clinica.local",
    "cargo": "MEDICO",
    "crm": "CRM-12345",
    "triggered_by_id": "admin-1"
  }
}
```

Essas rotas tambem sao usadas internamente pelo consumidor RabbitMQ do Agenda. O `usersService` publica envelopes no formato `{ "event": "...", "data": {...} }`; o Agenda usa `data.id` como id externo do medico/paciente e repassa `data.triggered_by_id` para auditoria/eventos.

Eventos aceitos:

| Evento | Routing key RabbitMQ | Endpoint manual equivalente | Efeito no Agenda |
| --- | --- | --- | --- |
| `MedicCreatedEvent` ou `UserCreatedEvent` com `cargo=MEDICO` | `users.doctor.created` | `POST /agenda/infra/events/users/doctor-created` | Cria doctor com `id_extern=data.id` e `name=data.userName` ou `data.name`. |
| `PacientCreatedEvent` ou `UserCreatedEvent` com `cargo=PACIENTE` | `users.patient.created` | `POST /agenda/infra/events/users/patient-created` | Cria patient com `id=data.id` e `name=data.userName` ou `data.name`. |
| `MedicDeletedEvent` ou `UserDeletedEvent` com `cargo=MEDICO` | `users.doctor.deleted` | `POST /agenda/infra/events/users/doctor-deleted` | Remove doctor pelo mesmo `data.id` recebido do `usersService`. |
| `PacientDeletedEvent` ou `UserDeletedEvent` com `cargo=PACIENTE` | `users.patient.deleted` | `POST /agenda/infra/events/users/patient-deleted` | Remove patient pelo mesmo `data.id` recebido do `usersService`. |

Exemplo de criacao de paciente:

```json
{
  "event": "PacientCreatedEvent",
  "data": {
    "id": "patient-1",
    "userName": "joao.paciente",
    "name": "Joao Paciente",
    "email": "joao@example.com",
    "cargo": "PACIENTE",
    "cpf": "12345678901",
    "triggered_by_id": "admin-1"
  }
}
```

Exemplo de delecao de medico:

```json
{
  "event": "MedicDeletedEvent",
  "data": {
    "id": "medic-1",
    "cargo": "MEDICO",
    "triggered_by_id": "admin-1"
  }
}
```

Exemplo de delecao de paciente:

```json
{
  "event": "PacientDeletedEvent",
  "data": {
    "id": "patient-1",
    "cargo": "PACIENTE",
    "triggered_by_id": "admin-1"
  }
}
```

Retorno esperado do handler:

```json
{
  "handled": true,
  "entity": "doctor",
  "external_id": "medic-1",
  "reason": null
}
```

## Notification Service

Base URL: `http://localhost:8003`

As notificacoes sao geradas por eventos consumidos do RabbitMQ. As rotas abaixo consultam ou atualizam essas notificacoes.

| Metodo | Endpoint | Entrada | Retorno esperado |
| --- | --- | --- | --- |
| `GET` | `/health` | Nenhuma. | Health do servico. |
| `GET` | `/notifications/users/{user_id}` | Path `user_id`; query `limit` 1-200, `unread_only` boolean. | Lista de notificacoes. |
| `GET` | `/notifications/users/{user_id}/bell` | Path `user_id`. | Resumo para sino/notificacoes do usuario. |
| `GET` | `/notifications/users/{user_id}/unread-count` | Path `user_id`. | `{"user_id":"...","unread":0}` |
| `GET` | `/notifications/patients/{patient_id}` | Path `patient_id`; query `limit`, `unread_only`. | Lista. |
| `GET` | `/notifications/patients/{patient_id}/bell` | Path `patient_id`. | Resumo. |
| `GET` | `/notifications/pacients/{patient_id}` | Alias legado de patients. | Lista. |
| `GET` | `/notifications/pacients/{patient_id}/bell` | Alias legado de patients. | Resumo. |
| `GET` | `/notifications/medics/{doctor_id}` | Path `doctor_id`; query `limit`, `unread_only`. | Lista. |
| `GET` | `/notifications/medics/{doctor_id}/bell` | Path `doctor_id`. | Resumo. |
| `GET` | `/notifications/doctors/{doctor_id}` | Alias de medics. | Lista. |
| `GET` | `/notifications/doctors/{doctor_id}/bell` | Alias de medics. | Resumo. |
| `GET` | `/notifications/admins` | Query `limit`, `unread_only`. | Lista de notificacoes admin. |
| `GET` | `/notifications/admins/bell` | Nenhuma. | Resumo admin. |
| `GET` | `/notifications/admins/{admin_id}` | Path `admin_id`; query `limit`, `unread_only`. | Lista admin. |
| `GET` | `/notifications/admins/{admin_id}/bell` | Path `admin_id`. | Resumo admin. |
| `GET` | `/notifications/{notification_id}` | Path `notification_id`. | Notificacao ou `404`. |
| `PATCH` | `/notifications/{notification_id}/read` | Path `notification_id`. | Notificacao marcada como lida ou `404`. |
| `WS` | `/ws/events` | WebSocket. | Eventos brutos. |
| `WS` | `/ws/notifications` | WebSocket. | Notificacoes em tempo real. |

WebSockets:

| Endpoint | O que envia | Payload esperado |
| --- | --- | --- |
| `/ws/events` | Todo evento RabbitMQ recebido pelo Notification Service, mesmo quando nao gera notificacao. | `{ "event": "event.received", "routing_key": "...", "data": { "event": "...", "data": {...} } }` |
| `/ws/notifications` | Apenas notificacoes persistidas/criadas pelo Notification Service. | `{ "event": "notification.created", "routing_key": "...", "data": { ...notification... } }` |

Exemplo:

```bash
curl "http://localhost:8003/notifications/users/1?limit=20&unread_only=true"
```

Formato esperado de notificacao:

```json
{
  "id": "notification-1",
  "user_id": "1",
  "title": "Consulta atualizada",
  "message": "Sua consulta foi alterada",
  "read": false,
  "created_at": "2026-06-09T10:00:00Z",
  "metadata": {}
}
```

## Analytic Service

Base URL: `http://localhost:8005`

| Metodo | Endpoint | Entrada | Retorno esperado |
| --- | --- | --- | --- |
| `GET` | `/analytics/health` | Nenhuma. | `{"status":"ok"}` |
| `GET` | `/analytics/events` | Query `limit`, inteiro entre 1 e 500, default 100. | Lista de eventos recentes. |
| `GET` | `/analytics/events/summary` | Nenhuma. | Lista agregada por origem/tipo. |
| `GET` | `/analytics/metrics` | Nenhuma. | Texto Prometheus. |
| `GET` | `/metrics` | Nenhuma. | Metricas HTTP do servico. |

Exemplo:

```bash
curl "http://localhost:8005/analytics/events?limit=50"
```

Evento esperado:

```json
{
  "id": "event-1",
  "source": "agenda-service",
  "event": "appointment.created",
  "payload": {},
  "created_at": "2026-06-09T10:00:00Z"
}
```

Resumo esperado:

```json
[
  {
    "source": "agenda-service",
    "event": "appointment.created",
    "count": 10
  }
]
```

## Observabilidade

Todos os servicos instrumentados expõem:

```text
GET /metrics
```

O retorno e texto no formato Prometheus, por exemplo:

```text
service_http_requests_total{service="agenda-service",method="GET",path="/docs",status="200"} 1
```

## Onde confirmar o contrato em tempo real

Use estes endpoints quando quiser ver o contrato exato gerado pela aplicacao em execucao:

```text
http://localhost:8000/openapi.json
http://localhost:8001/openapi.json
http://localhost:8002/openapi.json
http://localhost:8003/openapi.json
http://localhost:8005/openapi.json
```

## Contratos de mensageria

Todos os eventos seguem o envelope JSON:

```json
{
  "event": "NomeDoEvento",
  "data": {}
}
```

| Producer | Exchange | Routing keys principais | Consumers | Observacao |
| --- | --- | --- | --- | --- |
| Users Service | `users.events` | `users.doctor.created`, `users.doctor.deleted`, `users.patient.created`, `users.patient.deleted`, `users.admin.*`, `users.attendant.*`, `users.user.*`, `users.profile-image.updated` | Agenda, Notification, Analytics | Agenda consome apenas criacao/delecao de doctor/patient para manter espelho local. |
| Agenda Service | `agenda.events` | `agenda.appointment.*`, `agenda.doctor.*`, `agenda.patient.*`, `agenda.calendar.*`, `agenda.clinic.*`, `agenda.room.*`, `agenda.rule.*` | Notification, Analytics | Notification cria notificacoes especializadas para appointment created/updated e doctor created; outros eventos podem virar notificacoes genericas se tiverem recipient no payload. |

Consumers:

| Consumer | Queue | Exchanges bindados | Routing keys | Comportamento |
| --- | --- | --- | --- | --- |
| Agenda user events consumer | `agenda.user-events` | `users.events` | `users.doctor.created`, `users.patient.created`, `users.doctor.deleted`, `users.patient.deleted` | Cria/remove doctors e patients usando `data.id` do Users Service. |
| Notification consumer | `notification.events` | `users.events`, `agenda.events` | `#` por default, configuravel por `NOTIFICATION_EVENT_ROUTING_KEYS` | Persiste log de evento, transmite `/ws/events` e cria notificacoes quando houver destinatario/regra. |
| Analytics consumer | `analytic.events` | `users.events`, `agenda.events` | `#` por default, configuravel por `ANALYTIC_EVENT_ROUTING_KEYS` | Persiste eventos para consultas e metricas. |

Analise de consistencia:

| Item | Status |
| --- | --- |
| `usersService` -> `agendaService` para doctor/patient | Condizente. Routing keys e payloads batem com os handlers do Agenda. |
| `agendaService` -> `notificationService` | Condizente. Notification consome `agenda.events` e entende `agenda.appointment.created`/`agenda.appointment.updated`. |
| `usersService`/`agendaService` -> `analyticService` | Condizente. Analytics consome os dois exchanges com wildcard `#`. |
| WebSocket do Notification Service | Condizente apos ajuste: `/ws/events` recebe eventos brutos e `/ws/notifications` recebe notificacoes criadas. |
