from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import FastAPI

from src.api.router import api_router
from src.api.provider import get_event_bus, get_user_service_created_events_consumer
from src.infra.clients import DatadogClient
from src.infra.config.settings import settings
from src.infra.migrations import MigrationRunner
from src.observability import setup_observability


DatadogClient().configure()
logger = logging.getLogger(__name__)


async def _start_user_events_consumer_forever() -> None:
    consumer = get_user_service_created_events_consumer()
    retry_interval = max(1.0, settings.event_broker_retry_interval_seconds)

    while True:
        try:
            await consumer.start()
            logger.info("agenda RabbitMQ user events consumer started")
            return
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning(
                "agenda RabbitMQ consumer did not start; retrying in %.1fs: %s",
                retry_interval,
                exc,
            )
            await asyncio.sleep(retry_interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    MigrationRunner().run()
    event_bus = get_event_bus()
    event_bus.start()
    consumer_task = asyncio.create_task(_start_user_events_consumer_forever())
    yield
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    await get_user_service_created_events_consumer().stop()
    await event_bus.stop()


app = FastAPI(
    title="Agenda Service",
    version="1.0.0",
    description=(
        "Servico de agendamento medico. Expoe appointments, rooms, calendars, "
        "clinics, rules administrativas, health/readiness e websocket de eventos."
    ),
    openapi_tags=[
        {"name": "Appointments", "description": "Criacao, consulta, listagem por paciente/medico e tipos de appointment."},
        {"name": "Rooms", "description": "Rooms da agenda, incluindo detalhes administrativos com rules e appointments."},
        {"name": "Calendars", "description": "Calendario, dias do mes para o frontend e atualizacao de disponibilidade do dia."},
        {"name": "Rules", "description": "Rules genericas, semanais, especificas, por dia e contexto administrativo."},
        {"name": "Clinics", "description": "Clinicas e rules associadas."},
        {"name": "Infra", "description": "Health, readiness e handlers manuais para eventos do Users Service."},
        {"name": "Websocket", "description": "Stream websocket dos eventos da agenda."},
        {"name": "observability", "description": "Metricas Prometheus do service."},
    ],
    lifespan=lifespan,
)

app.include_router(api_router)
setup_observability(app, "agenda-service")


def main():
    import uvicorn

    uvicorn.run("src.server:app", host="127.0.0.1", port=8000, reload=True)
