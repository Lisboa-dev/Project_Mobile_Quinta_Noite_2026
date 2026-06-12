import os

from src.infra.clients.base import ClientHealth
from src.infra.config.settings import settings


class DatadogClient:
    def configure(self) -> None:
        os.environ.setdefault("DD_SERVICE", settings.datadog_service)
        os.environ.setdefault("DD_ENV", settings.datadog_env)
        os.environ.setdefault("DD_VERSION", settings.datadog_version)
        os.environ.setdefault("DD_AGENT_HOST", settings.datadog_agent_host)
        os.environ.setdefault("DD_TRACE_AGENT_PORT", str(settings.datadog_trace_agent_port))

        if not settings.datadog_enabled:
            return

        try:
            ddtrace = __import__("ddtrace")
            ddtrace.patch_all()
        except Exception:
            return

    def ping(self) -> ClientHealth:
        return ClientHealth(
            "datadog",
            True,
            metadata={
                "enabled": settings.datadog_enabled,
                "service": settings.datadog_service,
                "env": settings.datadog_env,
                "agent_host": settings.datadog_agent_host,
            },
        )
