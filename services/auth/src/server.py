import sys
import httpx
import orjson
import uvicorn

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette.middleware.base import BaseHTTPMiddleware

from config import get_settings
from .services.login import validateLoginService, loginService


# 🔥 HTTP client global (reuso de conexão)
client = httpx.AsyncClient(
    timeout=3.0,
    limits=httpx.Limits(
        max_connections=500,
        max_keepalive_connections=50
    ),
    http2=True
)


# 🔥 JSON rápido
def json_response(data, status=200):
    return Response(
        content=orjson.dumps(data),
        status_code=status,
        media_type="application/json"
    )




# 🔐 Middleware de autenticação (ForwardAuth core)
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        # 🔓 Rotas públicas (login)
        if request.url.path == "/auth/login":
            return await call_next(request)

        # 🔑 Pega token
        token = request.headers.get("authorization")

        if not token:
            return json_response({"error": "Missing token"}, 401)

        try:
            # ⚡ Validação externa (ou local, dependendo do teu service)
            is_valid = await validateLoginService(token)

            if not is_valid:
                return json_response({"error": "Invalid token"}, 403)

        except Exception:
            return json_response({"error": "Auth service failure"}, 500)

        # ✅ Liberado
        return await call_next(request)





# 🔐 Endpoint chamado pelo Traefik (ForwardAuth)
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

    # 🔥 MUITO IMPORTANTE:
    # headers retornados aqui podem ser propagados pelo Traefik
    return Response(
        status_code=200,
        headers={
            "X-User-Id": "123",   # exemplo
            "X-User-Role": "user"
        }
    )



# 🔐 Login (gera token)
async def login(request: Request):
    body = await request.json()
    token = await loginService(body)

    return json_response({"token": token})


# 🧱 App
app = Starlette(
    routes=[
        Route("/auth/validate", endpoint=forward_auth, methods=["GET"]),
        Route("/auth/login", endpoint=login, methods=["POST"]),
    ]
)

# 🔥 Middleware
app.add_middleware(AuthMiddleware)


# 🚀 Startup / Shutdown (boa prática com httpx)
@app.on_event("shutdown")
async def shutdown():
    await client.aclose()


def start():
    settings = get_settings()

    loop_type = "uvloop" if sys.platform != "win32" else "asyncio"

    uvicorn.run(
        "src.server:app",  
        host="0.0.0.0",
        port=settings.PORT,
        loop=loop_type,
        http="httptools",
        lifespan="on",
        reload=False
    )


if __name__ == "__main__":
    start()