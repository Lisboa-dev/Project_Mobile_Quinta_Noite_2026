from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI

from src.api.router import router as api_router
from src.infra.database import NotificationRepository, init_db
from src.infra.messaging import RabbitMQConsumer
from src.infra.websocket import events_hub, notifications_hub
from src.observability import setup_observability
from src.services import NotificationDispatcher, NotificationQueryService


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    repository = NotificationRepository()
    dispatcher = NotificationDispatcher(
        repository=repository,
        notifications_hub=notifications_hub,
        events_hub=events_hub,
    )
    consumer = RabbitMQConsumer()

    app.state.notification_query_service = NotificationQueryService(repository=repository)
    app.state.notification_dispatcher = dispatcher
    app.state.rabbitmq_consumer = consumer

    consumer_task = asyncio.create_task(consumer.start(dispatcher.dispatch_event))
    app.state.rabbitmq_consumer_task = consumer_task
    try:
        yield
    finally:
        consumer_task.cancel()
        await consumer.close()


app = FastAPI(
    title="Notification Service",
    version="1.0.0",
    description=(
        "Servico de notificacoes orientado por eventos. Consulta notificacoes por usuario, "
        "paciente, medico ou admin, marca leitura e transmite eventos por websocket."
    ),
    openapi_tags=[
        {"name": "health", "description": "Healthcheck do Notification Service."},
        {"name": "notifications", "description": "Consultas, bell summaries, unread count e marcacao de leitura."},
        {"name": "websocket", "description": "Streams websocket para eventos brutos e notificacoes criadas."},
        {"name": "observability", "description": "Metricas Prometheus do service."},
    ],
    lifespan=lifespan,
)

app.include_router(api_router)
setup_observability(app, "notification-service")


def main():
    import uvicorn

    uvicorn.run("src.server:app", host="127.0.0.1", port=8003, reload=True)
