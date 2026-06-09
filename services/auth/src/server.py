import sys
import json
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from .config import get_settings
from .services.authorization import authorization_service
from .services.event_log import init_db
from .services.login import validateLoginService
from .services.login import loginService
from .observability import setup_observability
from .services.tokenJwt import TokenService


def json_response(data, status=200):
    return Response(
        content=json.dumps(data).encode("utf-8"),
        status_code=status,
        media_type="application/json",
    )


def _strip_bearer(token: str) -> str:
    parts = token.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return token.strip()


async def forward_auth(request: Request):
    token = request.headers.get("authorization")

    if not token:
        return Response(status_code=401)

    try:
        is_valid = await validateLoginService(token)
        if not is_valid:
            return Response(status_code=403)
    except Exception:
        return Response(status_code=500)

    payload = TokenService.decode_token(_strip_bearer(token))
    if not payload:
        return Response(status_code=403)

    decision = await authorization_service.authorize(request, payload)
    if not decision.allowed:
        return Response(status_code=403, headers={"X-Authz-Reason": decision.reason or "forbidden"})

    return Response(
        status_code=200,
        headers={
            "X-User-Id": str(payload.get("sub", "")),
            "X-User-Role": str(payload.get("role", "")),
        },
    )


async def login(request: Request):
    try:
        body = await request.json()
        result = await loginService(body)
    except ValueError as exc:
        return json_response({"error": str(exc)}, 400)
    except Exception:
        return json_response({"error": "invalid request"}, 400)

    if not result:
        return json_response({"error": "invalid credentials"}, 401)

    return json_response(result)


async def health(_request: Request):
    return json_response({"status": "ok", "service": get_settings().APP_NAME})


@asynccontextmanager
async def lifespan(_app):
    init_db()
    yield


app = FastAPI(
    title="Auth Service",
    version="0.1.0",
    description="Servico de autenticacao e autorizacao.",
    lifespan=lifespan,
)
app.add_api_route("/health", endpoint=health, methods=["GET"])
app.add_api_route("/auth/validate", endpoint=forward_auth, methods=["GET"])
app.add_api_route("/auth/login", endpoint=login, methods=["POST"])
setup_observability(app, get_settings().APP_NAME)


def start():
    settings = get_settings()
    loop_type = "uvloop" if sys.platform != "win32" else "asyncio"

    uvicorn.run(
        "src.server:app",
        host="0.0.0.0",
        port=settings.PORT,
        loop=loop_type,
        lifespan="on",
        reload=False,
    )


if __name__ == "__main__":
    start()
