import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import router
from src.infra.database import EventLogRepository, init_db
from src.infra.messaging import RabbitMQConsumer
from src.observability import setup_observability
from src.services import EventIngestionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    service = EventIngestionService(EventLogRepository())
    consumer = RabbitMQConsumer()
    consumer_task = asyncio.create_task(consumer.start(service.ingest))

    app.state.event_ingestion_service = service
    app.state.rabbitmq_consumer = consumer
    app.state.rabbitmq_consumer_task = consumer_task
    try:
        yield
    finally:
        consumer_task.cancel()
        await consumer.close()


app = FastAPI(
    title="Analytic Service",
    version="0.1.0",
    description="Servico de analytics orientado por eventos.",
    lifespan=lifespan,
)
app.include_router(router)
setup_observability(app, "analytic-service")
