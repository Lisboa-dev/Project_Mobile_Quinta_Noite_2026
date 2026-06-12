import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_env() -> None:
    service_root = Path(__file__).resolve().parents[3]
    if len(service_root.parents) > 1:
        _load_dotenv_file(service_root.parents[1] / ".env")
    _load_dotenv_file(service_root / ".env")


load_env()


@dataclass(frozen=True)
class AgendaSettings:
    app_name: str = os.getenv("AGENDA_APP_NAME", "agenda-service")
    env: str = os.getenv("ENV", "development")
    database_url: str = os.getenv("AGENDA_DATABASE_URL", "postgresql://postgres:password@agenda-postgres:5432/agendadb")
    rabbitmq_url: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    rabbitmq_exchange: str = os.getenv("RABBITMQ_EXCHANGE", "agenda.events")
    user_events_exchange: str = os.getenv("USER_EVENTS_EXCHANGE", "users.events")
    user_events_queue: str = os.getenv("AGENDA_USER_EVENTS_QUEUE", "agenda.user-events")
    user_doctor_created_routing_key: str = os.getenv("USER_DOCTOR_CREATED_ROUTING_KEY", "users.doctor.created")
    user_patient_created_routing_key: str = os.getenv("USER_PATIENT_CREATED_ROUTING_KEY", "users.patient.created")
    user_doctor_deleted_routing_key: str = os.getenv("USER_DOCTOR_DELETED_ROUTING_KEY", "users.doctor.deleted")
    user_patient_deleted_routing_key: str = os.getenv("USER_PATIENT_DELETED_ROUTING_KEY", "users.patient.deleted")
    redis_url: str = os.getenv("AGENDA_REDIS_URL", os.getenv("REDIS_URL", "redis://agenda-redis:6379/0"))
    prometheus_url: str = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
    datadog_enabled: bool = os.getenv("DD_TRACE_ENABLED", "false").lower() in {"1", "true", "yes"}
    datadog_service: str = os.getenv("DD_SERVICE", "agenda-service")
    datadog_env: str = os.getenv("DD_ENV", os.getenv("ENV", "development"))
    datadog_version: str = os.getenv("DD_VERSION", "0.1.0")
    datadog_agent_host: str = os.getenv("DD_AGENT_HOST", "datadog")
    datadog_trace_agent_port: int = int(os.getenv("DD_TRACE_AGENT_PORT", "8126"))
    client_timeout_seconds: int = int(os.getenv("AGENDA_CLIENT_TIMEOUT_SECONDS", "3"))
    redis_cache_ttl_seconds: int = int(os.getenv("AGENDA_REDIS_CACHE_TTL_SECONDS", "300"))
    event_broker_buffer_max_size: int = int(os.getenv("AGENDA_EVENT_BROKER_BUFFER_MAX_SIZE", "1000"))
    event_broker_retry_interval_seconds: float = float(os.getenv("AGENDA_EVENT_BROKER_RETRY_INTERVAL_SECONDS", "5"))
    event_broker_retry_batch_size: int = int(os.getenv("AGENDA_EVENT_BROKER_RETRY_BATCH_SIZE", "50"))


settings = AgendaSettings()
