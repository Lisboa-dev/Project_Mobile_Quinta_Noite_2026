from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


SERVICES = {
    "agendaService": PROJECT_ROOT / "services" / "agendaService",
    "usersService": PROJECT_ROOT / "services" / "usersService",
    "auth": PROJECT_ROOT / "services" / "auth",
    "notificationService": PROJECT_ROOT / "services" / "notificationService",
    "analyticService": PROJECT_ROOT / "services" / "analyticService",
}


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class GlobalTestConfig:
    project_root: Path = PROJECT_ROOT
    services: dict[str, Path] | None = None
    use_mock_data: bool = True
    use_real_services: bool = False

    @classmethod
    def from_env(cls) -> "GlobalTestConfig":
        return cls(
            services=SERVICES,
            use_mock_data=env_flag("TEST_USE_MOCK_DATA", True),
            use_real_services=env_flag("TEST_USE_REAL_SERVICES", False),
        )


class GlobalTestProvider:
    def __init__(self, config: GlobalTestConfig | None = None):
        self.config = config or GlobalTestConfig.from_env()

    @property
    def services(self) -> dict[str, Path]:
        return self.config.services or SERVICES

    def service_path(self, service_name: str) -> Path:
        try:
            return self.services[service_name]
        except KeyError as exc:
            available = ", ".join(sorted(self.services))
            raise ValueError(f"Unknown service '{service_name}'. Available: {available}") from exc

    def env_for_service(self, service_name: str) -> dict[str, str]:
        env = os.environ.copy()
        env.setdefault("ENV", "test")
        env.setdefault("TEST_USE_MOCK_DATA", "true" if self.config.use_mock_data else "false")
        env.setdefault("TEST_USE_REAL_SERVICES", "true" if self.config.use_real_services else "false")
        env["PYTHONPATH"] = os.pathsep.join(
            [
                str(self.service_path(service_name) / "src"),
                str(self.service_path(service_name)),
            ]
        )
        return env


global_test_provider = GlobalTestProvider()
