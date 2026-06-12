import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OPENFGA_API_URL = os.getenv("OPENFGA_API_URL", "http://openfga:8080").rstrip("/")
OPENFGA_STORE_NAME = os.getenv("OPENFGA_STORE_NAME", "agendamento-medico")
MODEL_PATH = Path(os.getenv("OPENFGA_MODEL_PATH", "/openfga/authorization-model.json"))
TUPLES_PATH = Path(os.getenv("OPENFGA_TUPLES_PATH", "/openfga/tuples.json"))
WAIT_TIMEOUT_SECONDS = int(os.getenv("OPENFGA_WAIT_TIMEOUT_SECONDS", "60"))


def request_json(method: str, path: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        f"{OPENFGA_API_URL}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=10) as response:
        content = response.read()
        return json.loads(content.decode("utf-8")) if content else {}


def wait_for_openfga() -> None:
    deadline = time.time() + WAIT_TIMEOUT_SECONDS
    last_error = None
    while time.time() < deadline:
        try:
            request_json("GET", "/stores")
            return
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            time.sleep(2)
    raise RuntimeError(f"OpenFGA is not ready: {last_error}")


def get_or_create_store() -> str:
    stores = request_json("GET", "/stores").get("stores", [])
    for store in stores:
        if store.get("name") == OPENFGA_STORE_NAME:
            return str(store["id"])

    created = request_json("POST", "/stores", {"name": OPENFGA_STORE_NAME})
    return str(created["id"])


def write_authorization_model(store_id: str) -> None:
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    response = request_json("POST", f"/stores/{store_id}/authorization-models", model)
    print(f"OpenFGA authorization model ready: {response.get('authorization_model_id', 'latest')}")


def write_tuples(store_id: str) -> None:
    tuples = json.loads(TUPLES_PATH.read_text(encoding="utf-8"))
    tuple_keys = tuples.get("writes", {}).get("tuple_keys", [])
    for tuple_key in tuple_keys:
        try:
            request_json("POST", f"/stores/{store_id}/write", {"writes": {"tuple_keys": [tuple_key]}})
        except HTTPError as exc:
            if exc.code == 400:
                print(f"OpenFGA tuple already exists; continuing: {tuple_key}")
                continue
            raise
    print("OpenFGA initial tuples ready.")


def main() -> int:
    wait_for_openfga()
    store_id = get_or_create_store()
    print(f"OpenFGA store ready: {OPENFGA_STORE_NAME} ({store_id})")
    write_authorization_model(store_id)
    write_tuples(store_id)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"OpenFGA bootstrap failed: {exc}", file=sys.stderr)
        raise
