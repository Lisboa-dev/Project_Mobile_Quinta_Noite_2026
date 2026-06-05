from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from src.api.router import api_router
from src.api.provider import get_user_service_created_events_consumer
from src.infra.clients import DatadogClient
from src.infra.migrations import MigrationRunner


DatadogClient().configure()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    MigrationRunner().run()
    consumer = get_user_service_created_events_consumer()
    try:
        await consumer.start()
    except Exception:
        logger.exception("agenda RabbitMQ consumer did not start")
    yield


app = FastAPI(
    title="Agenda Service",
    version="1.0.0",
    description="servico de agendamento de consultas medicas",
    lifespan=lifespan,
)

app.include_router(api_router)


def main():
    import uvicorn

    uvicorn.run("src.server:app", host="127.0.0.1", port=8000, reload=True)
