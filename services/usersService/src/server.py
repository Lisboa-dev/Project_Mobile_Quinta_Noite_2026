from contextlib import asynccontextmanager
import asyncio
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from src.api.controllers import routerAdmins, routerAtendents, routerClientConfig, routerMedics, routerPacients, routerUsersCrud
from src.api.provider import UserFactory
from src.infra.adapters.UserRepositorySqlAlchemy import UserRepository
from src.infra.config.db.liteSql.LiteSql import get_query, init_db
from src.infra.models.sqlAlchemy.UserSqlSchamy import CargoEnum, Doctor, Usuario
from src.observability import setup_observability
from src.modules.users.domain.valueObjects.PasswordVO import Password


class WebSocketHub:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, payload: dict) -> None:
        for websocket in list(self.connections):
            await websocket.send_json(payload)


hub = WebSocketHub()


def seed_users() -> None:
    seeds = [
        ("admin", "Admin Sistema", "admin@clinica.local", "Admin123!", CargoEnum.ADMIN, None),
        ("medico", "Dra. Ana Lima", "medico@clinica.local", "Medico123!", CargoEnum.MEDICO, "CRM-SEED-001"),
        ("paciente", "Joao Paciente", "paciente@clinica.local", "Paciente123!", CargoEnum.PACIENTE, None),
        ("atendente", "Atendente Clinica", "atendente@clinica.local", "Atendente123!", CargoEnum.ATENDENTE, None),
    ]
    with get_query() as session:
        for username, nome, email, password, cargo, crm in seeds:
            exists = session.query(Usuario).filter(Usuario.userName == username).first()
            if exists:
                if cargo == CargoEnum.MEDICO and crm and exists.doctor is None:
                    session.add(Doctor(id=str(uuid4()), user_id=exists.id, crm=crm))
                continue
            user = Usuario(
                id=str(uuid4()),
                userName=username,
                nome=nome,
                email=email,
                senha=Password(password).hash,
                cargo=cargo,
            )
            session.add(user)
            session.flush()
            if cargo == CargoEnum.MEDICO and crm:
                session.add(Doctor(id=str(uuid4()), user_id=user.id, crm=crm))


def _read_value(value):
    if isinstance(value, tuple):
        value = value[0] if len(value) == 1 else None
    return getattr(value, "valor", None) or getattr(value, "value", value)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_users()
    app.state.event_payloads = []
    loop = asyncio.get_running_loop()

    def on_event(payload: dict) -> None:
        app.state.event_payloads.append(payload)
        loop.create_task(hub.broadcast(payload))

    UserFactory.event_bus_factory().subscribe(on_event)
    yield


app = FastAPI(
    title="Users Service",
    version="1.0.0",
    description=(
        "Servico de usuarios. Gerencia usuarios, admins, medicos, atendentes, pacientes, "
        "imagens de perfil e lookup interno usado pelo Auth. Todos os IDs de entidade sao UUID string."
    ),
    openapi_tags=[
        {"name": "health", "description": "Healthcheck do Users Service."},
        {"name": "users", "description": "CRUD generico de usuarios e imagem de perfil."},
        {"name": "admins", "description": "Listagem, detalhe, promocao, rebaixamento e remocao de admins."},
        {"name": "medics", "description": "Criacao, listagem, detalhe e remocao de medicos."},
        {"name": "atendents", "description": "Criacao, listagem, detalhe e remocao de atendentes."},
        {"name": "pacients", "description": "Criacao, listagem, detalhe e remocao de pacientes."},
        {"name": "config", "description": "Configuracoes client-side, como limites de upload."},
        {"name": "lookup", "description": "Lookup interno por email ou username para autenticacao."},
        {"name": "observability", "description": "Metricas Prometheus do service."},
    ],
    lifespan=lifespan,
)

app.include_router(routerAdmins)
app.include_router(routerAtendents)
app.include_router(routerMedics)
app.include_router(routerPacients)
app.include_router(routerUsersCrud)
app.include_router(routerClientConfig)
setup_observability(app, "users-service")


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


@app.get("/user/", tags=["lookup"])
def lookup_user(email: str | None = None, name: str | None = None):
    repository = UserRepository()
    user = repository.find_by_email(email) if email else None
    if user is None and name:
        user = repository.find_by_username(name)
    if user is None:
        return []
    return [
        {
            "id": str(user.id),
            "email": user.email.value,
            "name": user.userName.value,
            "password": user.password.hash,
            "role": _read_value(user.cargo),
            "cargo": _read_value(user.cargo),
        }
    ]


@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    await hub.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=3004)
