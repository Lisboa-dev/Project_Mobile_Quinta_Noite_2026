# API endpoints dos services

Este guia descreve os endpoints HTTP expostos pelos services, a entrada esperada e o formato de resposta. A documentacao interativa de cada service fica em `/docs` e o schema bruto em `/openapi.json`.

## Base URLs

| Service | URL direta | OpenAPI |
| --- | --- | --- |
| Auth | `http://localhost:8000` | `http://localhost:8000/docs` |
| Agenda | `http://localhost:8001` | `http://localhost:8001/docs` |
| Users | `http://localhost:8002` | `http://localhost:8002/docs` |
| Notification | `http://localhost:8003` | `http://localhost:8003/docs` |
| Analytics | `http://localhost:8005` | `http://localhost:8005/docs` |

Via Traefik, use `http://localhost` com os prefixos `/auth`, `/agenda`, `/users`, `/notification` e `/analytics`.

Para consumo pelo Flutter client em `agenda_Client/medagenda`, veja tambem `docs/flutter-endpoints.md`.

## Padroes

Headers para JSON:

```http
Content-Type: application/json
Accept: application/json
```

Quando protegido pelo gateway:

```http
Authorization: Bearer <access_token>
```

IDs de entidade devem ser tratados como `string` UUID. Nao envie IDs numericos para users, doctors, patients, rooms, appointments, rules ou notifications.

Resposta padrao de validacao FastAPI:

```json
{
  "detail": [
    {
      "loc": ["body", "field"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

## Auth Service

Base URL: `http://localhost:8000`

### `GET /health`

Entrada: nenhuma.

Resposta `200`:

```json
{
  "status": "ok",
  "service": "auth-service"
}
```

### `POST /auth/login`

Entrada JSON. Envie `password` e pelo menos um identificador: `email` ou `name`.

```json
{
  "email": "admin@clinica.local",
  "password": "Admin123!"
}
```

ou:

```json
{
  "name": "admin",
  "password": "Admin123!"
}
```

Resposta `200`:

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "tokens": {
    "access_token": "<jwt>",
    "refresh_token": "<jwt>",
    "token_type": "Bearer"
  }
}
```

Erros esperados: `400` para body invalido ou incompleto, `401` para credenciais invalidas.

### `GET /auth/validate`

Entrada header:

```http
Authorization: Bearer <access_token>
```

Resposta `200`: body vazio, com headers:

```http
X-User-Id: 550e8400-e29b-41d4-a716-446655440000
X-User-Role: ADMIN
```

Erros esperados: `401` sem token, `403` token invalido ou sem permissao, `500` erro interno.

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

`cargo`: `ADMIN`, `MEDICO`, `ATENDENTE`, `PACIENTE`, `GERENTE`, `SUPERVISOR`.

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
  "id": "550e8400-e29b-41d4-a716-446655440000",
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
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "triggered_by_id": null,
  "event_name": "users.doctor.created",
  "message": null,
  "data": {}
}
```

### Endpoints

| Metodo | Endpoint | Entrada | Resposta |
| --- | --- | --- | --- |
| `GET` | `/health` | Nenhuma. | `{"status":"ok"}` |
| `GET` | `/metrics` | Nenhuma. | Texto Prometheus. |
| `GET` | `/config/client` | Nenhuma. | Config de upload de imagem. |
| `GET` | `/user/` | Query `email` ou `name`. | Lista com usuario para Auth ou `[]`. |
| `GET` | `/users/` | Nenhuma. | `UserResponse[]`. |
| `POST` | `/users/` | Body `UserCreateRequest`. | `201 UserResponse`; `409` em conflito. |
| `GET` | `/users/{user_id}` | Path `user_id` UUID string. | `UserResponse`; `404`. |
| `PUT` | `/users/{user_id}` | Path `user_id`; body `UserUpdateRequest`. | `UserResponse`; `404`. |
| `DELETE` | `/users/{user_id}` | Path `user_id`. | `204`; `404`. |
| `POST` | `/users/{user_id}/profile-image` | `multipart/form-data`, campo `file`. | `UserResponse`; `400`; `404`. |
| `DELETE` | `/users/{user_id}/profile-image` | Path `user_id`. | `UserResponse`; `404`. |
| `GET` | `/admins/` | Nenhuma. | `UserResponse[]`. |
| `GET` | `/admins/{user_id}` | Path `user_id`. | `UserResponse`; `404`. |
| `POST` | `/admins/{user_id}/promote` | Path `user_id`. | `UseCaseResponse`; `404`. |
| `POST` | `/admins/doctors` | Body `MedicCreateRequest`. | `201 UseCaseResponse`; `409`. |
| `POST` | `/admins/{user_id}/depreciate` | Path `user_id`. | `UseCaseResponse`; `404`. |
| `DELETE` | `/admins/{user_id}` | Path `user_id`. | `204`; `404`. |
| `GET` | `/atendents/` | Nenhuma. | `UserResponse[]`. |
| `POST` | `/atendents/` | Body `AtendenteCreateRequest`. | `201 UseCaseResponse`; `409`. |
| `GET` | `/atendents/{user_id}` | Path `user_id`. | `UserResponse`; `404`. |
| `PUT` | `/atendents/{user_id}` | Path `user_id`; body `UserUpdateRequest`. | `501` enquanto nao implementado. |
| `DELETE` | `/atendents/{user_id}` | Path `user_id`. | `204`; `404`. |
| `GET` | `/medics/` | Nenhuma. | `UserResponse[]`. |
| `POST` | `/medics/` | Body `MedicCreateRequest`. | `201 UseCaseResponse`; `409`. |
| `GET` | `/medics/{user_id}` | Path `user_id`. | `UserResponse`; `404`. |
| `PUT` | `/medics/{user_id}` | Path `user_id`; body `UserUpdateRequest`. | `501` enquanto nao implementado. |
| `DELETE` | `/medics/{user_id}` | Path `user_id`. | `204`; `404`. |
| `GET` | `/pacients/` | Nenhuma. | `UserResponse[]`. |
| `POST` | `/pacients/` | Body `PacientCreateRequest`. | `201 UseCaseResponse`; `409`. |
| `GET` | `/pacients/{user_id}` | Path `user_id`. | `UserResponse`; `404`. |
| `PUT` | `/pacients/{user_id}` | Path `user_id`; body `UserUpdateRequest`. | `501` enquanto nao implementado. |
| `DELETE` | `/pacients/{user_id}` | Path `user_id`. | `204`; `404`. |
| `WS` | `/ws/events` | WebSocket. | Eventos publicados pelo Users Service. |

Resposta de `/user/`:

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "admin@clinica.local",
    "name": "admin",
    "password": "<hash>",
    "role": "ADMIN",
    "cargo": "ADMIN"
  }
]
```

## Agenda Service

Base URL: `http://localhost:8001`

Todas as rotas usam prefixo `/agenda`. Rooms e Rules exigem admin via gateway/header:

```http
X-User-Role: admin
```

Campos comuns de query:

| Campo | Tipo | Uso |
| --- | --- | --- |
| `limit` | int ou null | Limite de registros. |
| `offset` | int | Deslocamento, default `0`. |

### Appointments

`CreateAppointmentRequest`:

```json
{
  "scheduler_id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2026-06-10",
  "weekday": "wednesday",
  "doctor": "doctor-uuid",
  "patient": "patient-uuid",
  "time": "09:00",
  "type": "consulta",
  "triggered_by_id": "admin-uuid"
}
```

`UpdateAppointmentRequest`:

```json
{
  "triggered_by_id": "admin-uuid"
}
```

| Metodo | Endpoint | Entrada | Resposta |
| --- | --- | --- | --- |
| `POST` | `/agenda/appointments/` | Body `CreateAppointmentRequest`. | `201 {"created":true}`; `400`. |
| `GET` | `/agenda/appointments/` | Query `limit`, `offset`. | Lista de appointments. |
| `GET` | `/agenda/appointments/{appointment_id}` | Path `appointment_id`. | Appointment detalhado; `404`. |
| `PUT` | `/agenda/appointments/{appointment_id}` | Path `appointment_id`; body `UpdateAppointmentRequest`. | `{"updated":true}`; `404`. |
| `DELETE` | `/agenda/appointments/{appointment_id}` | Path `appointment_id`. | `204`. |
| `GET` | `/agenda/appointments/patient/{patient_id}` | Path `patient_id`; query `limit`, `offset`. | Lista cacheada de appointments do paciente. |
| `GET` | `/agenda/appointments/doctor/{doctor_id}` | Path `doctor_id`; query `limit`, `offset`. | Lista cacheada de appointments do medico. |
| `GET` | `/agenda/appointments/types/` | Query `limit`, `offset`. | Lista de tipos de appointment. |
| `GET` | `/agenda/appointments/types/{type_id}` | Path `type_id`. | Tipo de appointment; `404`. |

Exemplo de appointment em listagem:

```json
{
  "id": "appointment-uuid",
  "scheduler_id": "admin-uuid",
  "date": "2026-06-10",
  "weekday": "wednesday",
  "doctor": "doctor-uuid",
  "patient": "patient-uuid",
  "time": "09:00",
  "type": "consulta",
  "created_at": "2026-06-10T09:00:00Z"
}
```

Exemplo de appointment type:

```json
{
  "id": "type-uuid",
  "name": "Consulta inicial",
  "data": {
    "duration_minutes": 30,
    "color": "#2f80ed"
  },
  "created_at": "2026-06-10T09:00:00Z",
  "updated_at": "2026-06-10T09:00:00Z"
}
```

### Calendars

`CreateCalendarRequest`:

```json
{
  "mes": 6,
  "ano": 2026,
  "triggered_by_id": "admin-uuid"
}
```

`UpdateDayRequest`:

```json
{
  "data": {
    "available": true,
    "notes": "Atendimento normal"
  },
  "triggered_by_id": "admin-uuid"
}
```

| Metodo | Endpoint | Entrada | Resposta |
| --- | --- | --- | --- |
| `POST` | `/agenda/calendars/` | Body `CreateCalendarRequest`. | Resultado da criacao dos dias do mes. |
| `GET` | `/agenda/calendars/months/{year}/{month}/days` | Path `year`, `month`. | Dias do mes para o front, com `available`/`unavailable`. |
| `GET` | `/agenda/calendars/days` | Query `year`, `month`, `limit`, `offset`. | Lista cacheada de dias. |
| `GET` | `/agenda/calendars/days/{day_id}` | Path `day_id`. | Dia detalhado. |
| `PATCH` | `/agenda/calendars/days/{day_id}` | Path `day_id`; body `UpdateDayRequest`. | `{"updated":true,"day":{...}}` ou `{"updated":false}`. |
| `DELETE` | `/agenda/calendars/{ano}` | Path `ano`. | `204`. |

Resposta mensal esperada:

```json
[
  {
    "id": "day-uuid",
    "date": "2026-06-10",
    "year": 2026,
    "month": 6,
    "day": 10,
    "weekday": "wednesday",
    "available": true,
    "status": "available"
  }
]
```

### Clinics

`CreateClinicRequest`:

```json
{
  "name": "Clinica Central",
  "rules": [],
  "triggered_by_id": "admin-uuid"
}
```

`UpdateClinicRequest`:

```json
{
  "name": "Clinica Central - Unidade 2",
  "rules": [],
  "triggered_by_id": "admin-uuid"
}
```

| Metodo | Endpoint | Entrada | Resposta |
| --- | --- | --- | --- |
| `POST` | `/agenda/clinics/` | Body `CreateClinicRequest`. | `201 {"created":true}`. |
| `GET` | `/agenda/clinics/` | Query `limit`, `offset`. | Lista de clinics. |
| `GET` | `/agenda/clinics/{clinic_id}` | Path `clinic_id`. | Clinic detalhada; `404`. |
| `PUT` | `/agenda/clinics/{clinic_id}` | Path `clinic_id`; body `UpdateClinicRequest`. | `{"updated":true}`; `404`. |
| `DELETE` | `/agenda/clinics/{clinic_id}` | Path `clinic_id`. | `204`. |

### Rooms

`CreateRoomRequest`:

```json
{
  "name": "Sala 01",
  "triggered_by_id": "admin-uuid"
}
```

`UpdateRoomRequest`:

```json
{
  "name": "Sala 02",
  "disponibility": true,
  "rules": [],
  "triggered_by_id": "admin-uuid"
}
```

| Metodo | Endpoint | Entrada | Resposta |
| --- | --- | --- | --- |
| `POST` | `/agenda/rooms/` | Header admin; body `CreateRoomRequest`. | `201 {"created":true}`. |
| `GET` | `/agenda/rooms/` | Header admin; query `limit`, `offset`. | Lista de rooms. |
| `GET` | `/agenda/rooms/{room_id}` | Header admin; path `room_id`. | Room detalhada; `404`. |
| `PUT` | `/agenda/rooms/{room_id}` | Header admin; body `UpdateRoomRequest`. | `{"updated":true}`. |
| `DELETE` | `/agenda/rooms/{room_id}` | Header admin; path `room_id`. | `204`. |
| `GET` | `/agenda/rooms/admin/` | Header admin; query `limit`, `offset`. | Lista admin detalhada com `rules`, `appointments` e contadores. |
| `GET` | `/agenda/rooms/admin/{room_id}` | Header admin; path `room_id`. | Detalhe admin da room; `404`. |

Resposta admin de room:

```json
{
  "id": "room-uuid",
  "name": "Sala 01",
  "disponibility": true,
  "rules": [],
  "appointments": [],
  "appointments_count": 0
}
```

### Rules

`rangeTime` preferencial:

```json
{
  "start": "08:00",
  "end": "12:00"
}
```

| Metodo | Endpoint | Entrada | Resposta |
| --- | --- | --- | --- |
| `GET` | `/agenda/rules/` | Header admin; query `limit`, `offset`. | Lista de rules. |
| `GET` | `/agenda/rules/admin/context` | Header admin. | Contexto para criacao/delecao de rules por admin. |
| `GET` | `/agenda/rules/{rule_id}` | Header admin; path `rule_id`. | Rule detalhada. |
| `POST` | `/agenda/rules/block` | Header admin; body `CreateBlockRuleRequest`. | `201 {"created":true}`. |
| `POST` | `/agenda/rules/generic` | Header admin; body `CreateGenericRuleRequest`. | `201 {"created":true}`. |
| `POST` | `/agenda/rules/specific` | Header admin; body `CreateSpecificRuleRequest`. | `201 {"created":true}`. |
| `POST` | `/agenda/rules/specific-day` | Header admin; body `CreateSpecificDayRuleRequest`. | `201 {"created":true}`. |
| `POST` | `/agenda/rules/week` | Header admin; body `CreateWeekRuleRequest`. | `201 {"created":true}`. |
| `DELETE` | `/agenda/rules/{rule_id}` | Header admin; path `rule_id`. | `204`. |

`CreateBlockRuleRequest`:

```json
{
  "date": "2026-06-10",
  "weekday": null,
  "description": "Feriado",
  "target": "room-uuid",
  "targetType": "room",
  "nome": "Bloqueio feriado",
  "triggered_by_id": "admin-uuid"
}
```

`CreateGenericRuleRequest`:

```json
{
  "ruleEffect": "allow",
  "targetType": "doctor",
  "rangeTime": { "start": "08:00", "end": "12:00" },
  "description": "Atendimento pela manha",
  "nome": "Regra manha",
  "triggered_by_id": "admin-uuid"
}
```

`CreateSpecificRuleRequest`:

```json
{
  "ruleEffect": "deny",
  "target": "doctor-uuid",
  "targetType": "doctor",
  "rangeTime": { "start": "12:00", "end": "13:00" },
  "description": "Almoco",
  "nome": "Intervalo",
  "triggered_by_id": "admin-uuid"
}
```

`CreateSpecificDayRuleRequest`:

```json
{
  "ruleEffect": "allow",
  "rangeTime": { "start": "14:00", "end": "18:00" },
  "description": "Horario extra",
  "date": "2026-06-10",
  "target": "room-uuid",
  "targetType": "room",
  "nome": "Extra sala",
  "triggered_by_id": "admin-uuid"
}
```

`CreateWeekRuleRequest`:

```json
{
  "ruleEffect": "allow",
  "rangeTime": { "start": "08:00", "end": "17:00" },
  "description": "Horario semanal",
  "weekday": 1,
  "target": "doctor-uuid",
  "targetType": "doctor",
  "nome": "Segunda medico",
  "triggered_by_id": "admin-uuid"
}
```

Resposta de `/agenda/rules/admin/context`:

```json
{
  "generic": {
    "day": [],
    "doctor": [],
    "room": []
  },
  "specific": {
    "days": [],
    "doctors": [],
    "rooms": []
  },
  "targets": {
    "doctors": [],
    "rooms": []
  }
}
```

### Infra e websocket

`InfraEventRequest`:

```json
{
  "event": "MedicCreatedEvent",
  "data": {
    "id": "doctor-user-uuid",
    "userName": "dra.ana",
    "name": "Dra Ana",
    "email": "ana@clinica.local",
    "cargo": "MEDICO",
    "crm": "CRM-12345",
    "triggered_by_id": "admin-uuid"
  }
}
```

| Metodo | Endpoint | Entrada | Resposta |
| --- | --- | --- | --- |
| `GET` | `/agenda/infra/health` | Nenhuma. | Health do Agenda. |
| `GET` | `/agenda/infra/ready` | Nenhuma. | Readiness do Agenda. |
| `POST` | `/agenda/infra/events/users/doctor-created` | Body `InfraEventRequest`. | Resultado do handler. |
| `POST` | `/agenda/infra/events/users/patient-created` | Body `InfraEventRequest`. | Resultado do handler. |
| `POST` | `/agenda/infra/events/users/doctor-deleted` | Body `InfraEventRequest`. | Resultado do handler. |
| `POST` | `/agenda/infra/events/users/patient-deleted` | Body `InfraEventRequest`. | Resultado do handler. |
| `WS` | `/agenda/ws` | WebSocket. | Eventos `agenda.*` em tempo real. |
| `GET` | `/metrics` | Nenhuma. | Texto Prometheus. |

Resposta de handler:

```json
{
  "handled": true,
  "entity": "doctor",
  "external_id": "doctor-user-uuid",
  "reason": null
}
```

## Notification Service

Base URL: `http://localhost:8003`

Formato esperado de notification:

```json
{
  "id": "notification-uuid",
  "user_id": "user-uuid",
  "title": "Consulta atualizada",
  "message": "Sua consulta foi alterada",
  "read": false,
  "created_at": "2026-06-10T10:00:00Z",
  "metadata": {}
}
```

Formato de bell:

```json
{
  "unread": 2,
  "latest": []
}
```

| Metodo | Endpoint | Entrada | Resposta |
| --- | --- | --- | --- |
| `GET` | `/health` | Nenhuma. | Health do service. |
| `GET` | `/metrics` | Nenhuma. | Texto Prometheus. |
| `GET` | `/notifications/users/{user_id}` | Path `user_id`; query `limit` 1-200, `unread_only`. | Lista de notifications. |
| `GET` | `/notifications/users/{user_id}/bell` | Path `user_id`. | Resumo de sino do usuario. |
| `GET` | `/notifications/users/{user_id}/unread-count` | Path `user_id`. | `{"user_id":"user-uuid","unread":0}` |
| `GET` | `/notifications/patients/{patient_id}` | Path `patient_id`; query `limit`, `unread_only`. | Lista de notifications. |
| `GET` | `/notifications/patients/{patient_id}/bell` | Path `patient_id`. | Resumo de sino. |
| `GET` | `/notifications/pacients/{patient_id}` | Alias legado de `patients`. | Lista de notifications. |
| `GET` | `/notifications/pacients/{patient_id}/bell` | Alias legado de `patients`. | Resumo de sino. |
| `GET` | `/notifications/medics/{doctor_id}` | Path `doctor_id`; query `limit`, `unread_only`. | Lista de notifications. |
| `GET` | `/notifications/medics/{doctor_id}/bell` | Path `doctor_id`. | Resumo de sino. |
| `GET` | `/notifications/doctors/{doctor_id}` | Alias de `medics`. | Lista de notifications. |
| `GET` | `/notifications/doctors/{doctor_id}/bell` | Alias de `medics`. | Resumo de sino. |
| `GET` | `/notifications/admins` | Query `limit`, `unread_only`. | Lista de notifications admin. |
| `GET` | `/notifications/admins/bell` | Nenhuma. | Resumo admin geral. |
| `GET` | `/notifications/admins/{admin_id}` | Path `admin_id`; query `limit`, `unread_only`. | Lista de notifications do admin. |
| `GET` | `/notifications/admins/{admin_id}/bell` | Path `admin_id`. | Resumo do admin. |
| `GET` | `/notifications/{notification_id}` | Path `notification_id`. | Notification; `404`. |
| `PATCH` | `/notifications/{notification_id}/read` | Path `notification_id`. | Notification marcada como lida; `404`. |
| `WS` | `/ws/events` | WebSocket. | Eventos brutos recebidos do RabbitMQ. |
| `WS` | `/ws/notifications` | WebSocket. | Notifications persistidas/criadas em tempo real. |

Exemplo:

```bash
curl "http://localhost:8003/notifications/users/550e8400-e29b-41d4-a716-446655440000?limit=20&unread_only=true"
```

## Analytic Service

Base URL: `http://localhost:8005`

Evento esperado:

```json
{
  "id": "event-uuid",
  "source": "agenda-service",
  "event": "appointment.created",
  "payload": {},
  "created_at": "2026-06-10T10:00:00Z"
}
```

| Metodo | Endpoint | Entrada | Resposta |
| --- | --- | --- | --- |
| `GET` | `/analytics/health` | Nenhuma. | `{"status":"ok"}` |
| `GET` | `/analytics/events` | Query `limit`, int 1-500, default `100`. | Lista de eventos recentes. |
| `GET` | `/analytics/events/summary` | Nenhuma. | Agregado por `source` e `event`. |
| `GET` | `/analytics/metrics` | Nenhuma. | Texto Prometheus do analytics. |
| `GET` | `/metrics` | Nenhuma. | Metricas HTTP do service. |

Resposta de summary:

```json
[
  {
    "source": "agenda-service",
    "event": "appointment.created",
    "count": 10
  }
]
```

## Mensageria

Envelope padrao dos eventos:

```json
{
  "event": "NomeDoEvento",
  "data": {}
}
```

| Producer | Exchange | Routing keys principais | Consumers |
| --- | --- | --- | --- |
| Users Service | `users.events` | `users.doctor.created`, `users.doctor.deleted`, `users.patient.created`, `users.patient.deleted`, `users.admin.*`, `users.attendant.*`, `users.user.*`, `users.profile-image.updated` | Agenda, Notification, Analytics |
| Agenda Service | `agenda.events` | `agenda.appointment.*`, `agenda.doctor.*`, `agenda.patient.*`, `agenda.calendar.*`, `agenda.clinic.*`, `agenda.room.*`, `agenda.rule.*` | Notification, Analytics |

Eventos de Users aceitos pelo Agenda:

| Evento | Routing key | Efeito |
| --- | --- | --- |
| `MedicCreatedEvent` ou `UserCreatedEvent` com `cargo=MEDICO` | `users.doctor.created` | Cria doctor espelhado usando `data.id`. |
| `PacientCreatedEvent` ou `UserCreatedEvent` com `cargo=PACIENTE` | `users.patient.created` | Cria patient espelhado usando `data.id`. |
| `MedicDeletedEvent` ou `UserDeletedEvent` com `cargo=MEDICO` | `users.doctor.deleted` | Remove doctor espelhado por `data.id`. |
| `PacientDeletedEvent` ou `UserDeletedEvent` com `cargo=PACIENTE` | `users.patient.deleted` | Remove patient espelhado por `data.id`. |

## Onde confirmar o contrato em runtime

```text
http://localhost:8000/openapi.json
http://localhost:8001/openapi.json
http://localhost:8002/openapi.json
http://localhost:8003/openapi.json
http://localhost:8005/openapi.json
```
