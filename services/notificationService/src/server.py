from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from src.infra.database import init_db
from src.infra.messaging import hub, start_consumer_task
from src.modules.email.api.router import router as email_router
from src.modules.userBell.api.router import router as user_bell_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_consumer_task()
    yield


app = FastAPI(
    title="Notification Service",
    version="1.0.0",
    description="Servico de notificacoes orientado a features.",
    lifespan=lifespan,
)

app.include_router(email_router)
app.include_router(user_bell_router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


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

    uvicorn.run("src.server:app", host="127.0.0.1", port=8003, reload=True)
