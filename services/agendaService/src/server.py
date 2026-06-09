from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from src.api.router import api_router
from src.api.provider import get_event_bus, get_user_service_created_events_consumer
from src.infra.clients import DatadogClient
from src.infra.migrations import MigrationRunner
from src.observability import setup_observability


DatadogClient().configure()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    MigrationRunner().run()
    event_bus = get_event_bus()
    event_bus.start()
    consumer = get_user_service_created_events_consumer()
    try:
        await consumer.start()
    except Exception:
        logger.exception("agenda RabbitMQ consumer did not start")
    yield
    await event_bus.stop()


app = FastAPI(
    title="Agenda Service",
    version="1.0.0",
    description="servico de agendamento de consultas medicas",
    lifespan=lifespan,
)

app.include_router(api_router)
setup_observability(app, "agenda-service")


def main():
    import uvicorn

    uvicorn.run("src.server:app", host="127.0.0.1", port=8000, reload=True)
