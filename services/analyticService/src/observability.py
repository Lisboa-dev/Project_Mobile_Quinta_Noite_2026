import json
import logging
import time
from collections import defaultdict
from typing import Any

from fastapi import Request, Response


logger = logging.getLogger("observability")
BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)


class HttpMetrics:
    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        self.requests: dict[tuple[str, str, str], int] = defaultdict(int)
        self.duration_sum: dict[tuple[str, str], float] = defaultdict(float)
        self.duration_count: dict[tuple[str, str], int] = defaultdict(int)
        self.duration_buckets: dict[tuple[str, str, float], int] = defaultdict(int)

    def observe(self, method: str, path: str, status_code: int, duration_seconds: float) -> None:
        self.requests[(method, path, str(status_code))] += 1
        self.duration_sum[(method, path)] += duration_seconds
        self.duration_count[(method, path)] += 1
        for bucket in BUCKETS:
            if duration_seconds <= bucket:
                self.duration_buckets[(method, path, bucket)] += 1

    def render(self) -> str:
        lines = ["# HELP service_http_requests_total Total de requisicoes HTTP por servico.", "# TYPE service_http_requests_total counter"]
        for (method, path, status), total in sorted(self.requests.items()):
            lines.append('service_http_requests_total{service="%s",method="%s",path="%s",status="%s"} %s' % (self.service_name, method, path, status, total))
        lines.extend(["# HELP service_http_request_duration_seconds Duracao das requisicoes HTTP.", "# TYPE service_http_request_duration_seconds histogram"])
        for method, path in sorted(self.duration_count):
            for bucket in BUCKETS:
                cumulative = self.duration_buckets.get((method, path, bucket), 0)
                lines.append('service_http_request_duration_seconds_bucket{service="%s",method="%s",path="%s",le="%s"} %s' % (self.service_name, method, path, bucket, cumulative))
            lines.append('service_http_request_duration_seconds_bucket{service="%s",method="%s",path="%s",le="+Inf"} %s' % (self.service_name, method, path, self.duration_count[(method, path)]))
            lines.append('service_http_request_duration_seconds_sum{service="%s",method="%s",path="%s"} %.6f' % (self.service_name, method, path, self.duration_sum[(method, path)]))
            lines.append('service_http_request_duration_seconds_count{service="%s",method="%s",path="%s"} %s' % (self.service_name, method, path, self.duration_count[(method, path)]))
        lines.append('service_info{service="%s"} 1' % self.service_name)
        return "\n".join(lines) + "\n"


def _route_path(request: Request) -> str:
    route = request.scope.get("route")
    return str(getattr(route, "path", request.url.path))


def setup_observability(app, service_name: str) -> None:
    logging.basicConfig(level=logging.INFO)
    metrics = HttpMetrics(service_name)
    app.state.http_metrics = metrics

    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):
        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.perf_counter() - start
            path = _route_path(request)
            if path != "/metrics":
                metrics.observe(request.method, path, status_code, duration)
                logger.info(json.dumps({"service": service_name, "action": f"{request.method} {path}", "response": {"status_code": status_code}, "response_time_ms": round(duration * 1000, 2)}, ensure_ascii=False, default=str))

    @app.get("/metrics", tags=["observability"])
    def metrics_endpoint():
        return Response(metrics.render(), media_type="text/plain; version=0.0.4")
