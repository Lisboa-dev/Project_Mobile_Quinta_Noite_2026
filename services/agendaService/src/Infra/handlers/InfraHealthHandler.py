from typing import Any
from urllib.parse import urlsplit, urlunsplit

from src.infra.config.settings import settings


_HEALTHCHECK_PATH = "/agenda/infra/health"
_HEALTHCHECK_CONTAINER_PORT = 8000


def _mask_url(value: str) -> str:
    parsed = urlsplit(value)
    if not parsed.username and not parsed.password:
        return value

    host = parsed.hostname or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return urlunsplit((parsed.scheme, f"***:***@{host}", parsed.path, parsed.query, parsed.fragment))


class InfraHealthHandler:
    def __init__(self, event_bus: Any | None = None):
        self._event_bus = event_bus

    async def check(self) -> dict[str, Any]:
        return {
            "service": settings.app_name,
            "ok": True,
            "mode": "docker-liveness",
            "healthcheck": {
                "path": _HEALTHCHECK_PATH,
                "container_port": _HEALTHCHECK_CONTAINER_PORT,
                "policy": "Keep the application healthcheck local and delegate dependency readiness to Docker Compose.",
                "dependency_condition": "service_healthy",
            },
            "event_broker_buffer": self._event_bus.buffer_status() if self._event_bus else None,
            "dependencies": [
                {
                    "name": "rabbitmq",
                    "configured": True,
                    "healthcheck": "rabbitmq-diagnostics -q ping",
                    "url": _mask_url(settings.rabbitmq_url),
                    "exchange": settings.rabbitmq_exchange,
                    "user_events_exchange": settings.user_events_exchange,
                    "user_events_queue": settings.user_events_queue,
                },
                {
                    "name": "postgres",
                    "configured": True,
                    "healthcheck": "pg_isready",
                    "url": _mask_url(settings.database_url),
                },
                {
                    "name": "redis",
                    "configured": True,
                    "healthcheck": "redis-cli ping",
                    "url": _mask_url(settings.redis_url),
                },
                {
                    "name": "prometheus",
                    "configured": True,
                    "url": settings.prometheus_url,
                },
                {
                    "name": "datadog",
                    "configured": True,
                    "enabled": settings.datadog_enabled,
                    "service": settings.datadog_service,
                    "env": settings.datadog_env,
                    "agent_host": settings.datadog_agent_host,
                },
            ],
        }

    async def readiness(self) -> dict[str, Any]:
        broker_health = await self._event_bus.broker_health() if self._event_bus else None
        broker_ok = bool(broker_health.ok) if broker_health is not None else True
        return {
            "service": settings.app_name,
            "ok": broker_ok,
            "mode": "docker-readiness",
            "event_broker": (
                {
                    "name": broker_health.name,
                    "ok": broker_health.ok,
                    "detail": broker_health.detail,
                    "metadata": broker_health.metadata,
                }
                if broker_health is not None
                else None
            ),
            "event_broker_buffer": self._event_bus.buffer_status() if self._event_bus else None,
        }
