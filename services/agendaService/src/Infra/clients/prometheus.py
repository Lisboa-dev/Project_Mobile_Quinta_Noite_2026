import json
from urllib.parse import urlencode
from urllib.request import urlopen

from src.infra.clients.base import ClientHealth
from src.infra.config.settings import settings


class PrometheusClient:
    def __init__(self, base_url: str | None = None):
        self._base_url = (base_url or settings.prometheus_url).rstrip("/")

    def query(self, expression: str) -> dict:
        params = urlencode({"query": expression})
        with urlopen(f"{self._base_url}/api/v1/query?{params}", timeout=3) as response:
            return json.loads(response.read().decode("utf-8"))

    def ping(self) -> ClientHealth:
        try:
            data = self.query("up")
            status = str(data.get("status", "unknown"))
            return ClientHealth("prometheus", status == "success", metadata={"status": status})
        except Exception as exc:
            return ClientHealth("prometheus", False, str(exc))
