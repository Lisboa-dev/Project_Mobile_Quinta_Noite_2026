from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

try:
    from .providers import GlobalTestProvider, SERVICES
except ImportError:
    from providers import GlobalTestProvider, SERVICES


@dataclass(frozen=True)
class SuiteResult:
    name: str
    returncode: int


def _banner(title: str) -> None:
    line = "=" * 72
    print(f"\n{line}\n{title}\n{line}", flush=True)


def _run_command(name: str, path: Path, command: list[str], env: dict[str, str]) -> SuiteResult:
    _banner(f"TEST SUITE: {name}")
    result = subprocess.run(command, cwd=path, env=env)
    return SuiteResult(name=name, returncode=result.returncode)


@lru_cache(maxsize=1)
def _poetry_python(project_root: Path) -> str:
    result = subprocess.run(
        ["poetry", "-C", str(project_root), "env", "info", "-p"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return sys.executable

    venv_path = Path(result.stdout.strip())
    executable = venv_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return str(executable if executable.exists() else sys.executable)


def _pytest_command(target: str, provider: GlobalTestProvider, include_integration: bool) -> list[str]:
    command = [_poetry_python(provider.config.project_root), "-m", "pytest", target]
    if not include_integration:
        command.extend(["-m", "not integration"])
    return command


def run_global(provider: GlobalTestProvider, include_integration: bool = False) -> SuiteResult:
    env = os.environ.copy()
    env.setdefault("ENV", "test")
    env.setdefault("TEST_USE_MOCK_DATA", "true" if provider.config.use_mock_data else "false")
    env.setdefault("TEST_USE_REAL_SERVICES", "true" if provider.config.use_real_services else "false")
    env["PYTHONPATH"] = str(provider.config.project_root)
    return _run_command(
        "global",
        provider.config.project_root,
        _pytest_command("tests/global", provider, include_integration),
        env,
    )


def run_services(
    service_names: list[str],
    provider: GlobalTestProvider,
    include_integration: bool = False,
) -> list[SuiteResult]:
    results: list[SuiteResult] = []
    for service_name in service_names:
        service_path = provider.service_path(service_name)
        results.append(
            _run_command(
                service_name,
                service_path,
                _pytest_command("tests", provider, include_integration),
                provider.env_for_service(service_name),
            )
        )
    return results


def run_all(
    service_names: list[str] | None = None,
    include_global: bool = True,
    include_integration: bool = False,
) -> int:
    provider = GlobalTestProvider()
    names = service_names or list(SERVICES)
    results: list[SuiteResult] = []
    if include_global:
        results.append(run_global(provider, include_integration=include_integration))
    results.extend(run_services(names, provider, include_integration=include_integration))

    _banner("TEST SUMMARY")
    for result in results:
        status = "PASS" if result.returncode == 0 else f"FAIL ({result.returncode})"
        print(f"{result.name:<24} {status}", flush=True)
    return 0 if all(result.returncode == 0 for result in results) else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run monorepo test suites by service.")
    parser.add_argument("services", nargs="*", help="Services to test. Empty means all.")
    parser.add_argument("--services-only", action="store_true", help="Skip global provider tests.")
    parser.add_argument(
        "--include-integration",
        action="store_true",
        help="Include integration tests that may require Docker and external services.",
    )
    args = parser.parse_args(argv)
    invalid = sorted(set(args.services) - set(SERVICES))
    if invalid:
        parser.error(f"invalid service(s): {', '.join(invalid)}")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    return run_all(
        args.services or None,
        include_global=not args.services_only,
        include_integration=args.include_integration,
    )


if __name__ == "__main__":
    raise SystemExit(main())
