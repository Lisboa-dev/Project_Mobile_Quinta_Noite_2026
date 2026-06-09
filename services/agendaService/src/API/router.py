from fastapi import APIRouter

from src.api.controllers import (
    routerAppointment,
    routerCalendar,
    routerClinic,
    routerInfra,
    routerRoom,
    routerRule,
    routerWebsocket,
)


api_router = APIRouter(prefix="/agenda")

api_router.include_router(routerAppointment)
api_router.include_router(routerCalendar, include_in_schema=False)
api_router.include_router(routerClinic, include_in_schema=False)
api_router.include_router(routerInfra, include_in_schema=False)
api_router.include_router(routerRoom)
api_router.include_router(routerRule, include_in_schema=False)
api_router.include_router(routerWebsocket)

routerAgenda = api_router
