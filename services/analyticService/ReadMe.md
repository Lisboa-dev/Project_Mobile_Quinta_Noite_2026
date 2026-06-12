# Analytic Service

Servico de analytics orientado por feature/contexto.

## Contextos

- `modules/doctorDashboard`: dashboard do medico, com produtividade, fluxo de pacientes e proxima acao.
- `modules/operationsCenter`: contexto administrativo e operacional. Ele agrega o dashboard de negocio do admin e o dashboard de plataforma do sysAdmin.

## Stack open source

- FastAPI para API do servico.
- Prometheus para metricas.
- Grafana OSS para dashboards visuais.
- OpenTelemetry Collector para receber metricas distribuidas e exportar para Prometheus.

## Endpoints

- `GET /analytics/doctors/{doctor_id}/dashboard`
- `GET /analytics/operations/business/dashboard`
- `GET /analytics/operations/platform/dashboard`
- `GET /analytics/metrics`

Para subir a stack de observabilidade:

```bash
docker compose --profile observability up analytic-service prometheus grafana otel-collector
```
