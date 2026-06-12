# Flutter client endpoint guide

Aplicacao: `agenda_Client/medagenda`.

## Base URL por plataforma

Use `--dart-define=API_BASE_URL=...` quando rodar o Flutter:

```bash
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost
flutter run -d windows --dart-define=API_BASE_URL=http://localhost
flutter run -d android --dart-define=API_BASE_URL=http://10.0.2.2
```

O client centraliza endpoints em `lib/core/api/endpoints.dart` e chamadas em `lib/core/api/api_client.dart`.

## Headers autenticados

Depois do login, envie em todos os endpoints protegidos:

```http
Authorization: Bearer <access_token>
X-User-Id: <user_uuid>
X-User-Role: admin|doctor|atendent|user
```

`ApiClient` ja propaga esses headers.

## Cadastro publico

Tela: `Cadastre-se`.

O formulario publico nao deve exibir `cargo`. Todo cadastro publico cria paciente:

```http
POST /users/pacients/
```

Body:

```json
{
  "userName": "maria",
  "email": "maria@clinica.local",
  "name": "Maria",
  "password": "Senha123!",
  "cpf": "00000000000"
}
```

## Paciente

Hub: marketplace de medicos.

Endpoints usados:

| Funcao | Endpoint |
| --- | --- |
| Sino | `GET /notification/notifications/users/{user_id}` e `/unread-count` |
| Marketplace | `GET /users/medics/` |
| Agenda do medico | `GET /agenda/appointments/doctor/{doctor_id}` |
| Criar primeira consulta | `POST /agenda/appointments/` |

Regra de negocio no client: paciente cria apenas `type=consulta`. Retornos, exames e procedimentos ficam para doctor ou atendente.

## Atendente

Hub: `AtendentDashboardScreen`.

Funcionalidades:

| Funcao | Endpoint |
| --- | --- |
| Gerenciar appointments | `GET /agenda/appointments/`, `POST /agenda/appointments/` |
| Pesquisar pacientes | `GET /users/pacients/` |
| Pesquisar doctors | `GET /users/medics/` |
| Ver disponibilidade | `GET /agenda/appointments/` filtrando por data no client |

## Doctor

Hub: `DoctorDashboardScreen`.

Funcionalidades:

| Funcao | Endpoint |
| --- | --- |
| Listar appointments | `GET /agenda/appointments/doctor/{doctor_id}` |
| Criar regras para si | `POST /agenda/rules/generic`, `/week`, `/specific`, `/specific-day` com `type=doctor` |
| Dashboard | `GET /analytics/events/summary` e appointments filtrados |
| Tipos de consulta | `GET /agenda/appointments/types/` e, se exposto pelo backend, `POST /agenda/appointments/types/` |
| Sino | `GET /notification/notifications/medics/{doctor_id}` |

## Admin

Hub: `AdminDashboardScreen`.

Funcionalidades:

| Funcao | Endpoint |
| --- | --- |
| Tudo do atendente | `GET/POST /agenda/appointments/`, busca users |
| Listar/gerenciar pacientes | `GET /users/pacients/`, `DELETE /users/pacients/{id}` |
| Listar/gerenciar medicos | `GET /users/medics/`, `POST /users/medics/`, `DELETE /users/medics/{id}` |
| Listar/criar atendentes | `GET /users/atendents/`, `POST /users/atendents/` |
| Regras globais | `POST /agenda/rules/*` com `targetType=doctor|day|room` |
| Montar calendario | `POST /agenda/calendars/` |
| Dashboard | `GET /analytics/events/summary`, `GET /agenda/appointments/`, `GET /users/*` |

## Appointment create

Nao envie `room` nem `room_id`; o backend resolve sala internamente.

```json
{
  "scheduler_id": "user-uuid",
  "date": "2026-06-12",
  "weekday": "friday",
  "doctor": "doctor-uuid",
  "patient": "patient-uuid",
  "time": "09:00",
  "type": "consulta",
  "triggered_by_id": "user-uuid"
}
```
