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
    description=(
        "Servico de autenticacao e autorizacao. Emite tokens JWT no login e valida "
        "tokens para o gateway, devolvendo headers X-User-Id e X-User-Role."
    ),
    openapi_tags=[
        {"name": "health", "description": "Healthcheck do Auth Service."},
        {"name": "auth", "description": "Login, validacao de token e decisao de autorizacao."},
        {"name": "observability", "description": "Metricas HTTP do service."},
    ],
    lifespan=lifespan,
)
app.add_api_route(
    "/health",
    endpoint=health,
    methods=["GET"],
    tags=["health"],
    summary="Healthcheck do Auth Service",
    responses={200: {"description": "Servico saudavel", "content": {"application/json": {"example": {"status": "ok", "service": "auth-service"}}}}},
)
app.add_api_route(
    "/auth/validate",
    endpoint=forward_auth,
    methods=["GET"],
    tags=["auth"],
    summary="Valida token e permissao da requisicao",
    description="Usado pelo gateway. Espera Authorization: Bearer <token> e retorna headers X-User-Id e X-User-Role quando autorizado.",
    responses={
        200: {
            "description": "Token valido e acesso autorizado. Body vazio.",
            "headers": {
                "X-User-Id": {"schema": {"type": "string"}, "description": "UUID do usuario autenticado."},
                "X-User-Role": {"schema": {"type": "string"}, "description": "Role/cargo do usuario autenticado."},
            },
        },
        401: {"description": "Header Authorization ausente."},
        403: {"description": "Token invalido ou acesso negado."},
        500: {"description": "Erro interno durante validacao."},
    },
)
app.add_api_route(
    "/auth/login",
    endpoint=login,
    methods=["POST"],
    tags=["auth"],
    summary="Autentica usuario e retorna tokens JWT",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["password"],
                        "properties": {
                            "email": {"type": "string", "example": "admin@clinica.local"},
                            "name": {"type": "string", "example": "admin"},
                            "password": {"type": "string", "example": "Admin123!"},
                        },
                    },
                    "examples": {
                        "email": {"summary": "Login por email", "value": {"email": "admin@clinica.local", "password": "Admin123!"}},
                        "name": {"summary": "Login por username", "value": {"name": "admin", "password": "Admin123!"}},
                    },
                }
            },
        }
    },
    responses={
        200: {
            "description": "Login valido.",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "tokens": {
                            "access_token": "<jwt>",
                            "refresh_token": "<jwt>",
                            "token_type": "Bearer",
                        },
                    }
                }
            },
        },
        400: {"description": "Body invalido ou incompleto."},
        401: {"description": "Credenciais invalidas."},
    },
)
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
