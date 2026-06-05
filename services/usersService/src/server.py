from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from src.api.controllers import routerAdmins, routerAtendents, routerMedics, routerPacients
from src.api.Provider import UserFactory
from src.infra.adapters.UserRepositorySqlAlchemy import UserRepository
from src.infra.config.db.liteSql.LiteSql import get_query, init_db
from src.infra.models.sqlAlchemy.UserSqlSchamy import CargoEnum, Usuario
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
        ("admin", "Admin Sistema", "admin@clinica.local", "Admin123!", CargoEnum.ADMIN),
        ("medico", "Dra. Ana Lima", "medico@clinica.local", "Medico123!", CargoEnum.MEDICO),
        ("paciente", "Joao Paciente", "paciente@clinica.local", "Paciente123!", CargoEnum.PACIENTE),
        ("atendente", "Atendente Clinica", "atendente@clinica.local", "Atendente123!", CargoEnum.ATENDENTE),
    ]
    with get_query() as session:
        for username, nome, email, password, cargo in seeds:
            exists = session.query(Usuario).filter(Usuario.userName == username).first()
            if exists:
                continue
            session.add(
                Usuario(
                    userName=username,
                    nome=nome,
                    email=email,
                    senha=Password(password).hash,
                    cargo=cargo,
                )
            )


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


app = FastAPI(title="Users Service", lifespan=lifespan)

app.include_router(routerAdmins)
app.include_router(routerAtendents)
app.include_router(routerMedics)
app.include_router(routerPacients)


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
            "id": user.id,
            "email": user.email.value,
            "name": user.userName.value,
            "password": user.password.hash,
            "role": user.cargo.valor,
            "cargo": user.cargo.valor,
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
