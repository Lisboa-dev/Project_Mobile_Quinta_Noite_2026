from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.interfaces.infra import InfraEventRequest
from src.api.provider import (
    get_infra_health_handler,
    get_user_service_doctor_created_handler,
    get_user_service_doctor_deleted_handler,
    get_user_service_patient_created_handler,
    get_user_service_patient_deleted_handler,
)
from src.infra.handlers import (
    InfraHealthHandler,
    UserServiceDoctorCreatedHandler,
    UserServiceDoctorDeletedHandler,
    UserServicePatientCreatedHandler,
    UserServicePatientDeletedHandler,
)


routerInfra = APIRouter(prefix="/infra", tags=["Infra"])


@routerInfra.get("/health")
async def infra_health(handler: InfraHealthHandler = Depends(get_infra_health_handler)):
    return await handler.check()


@routerInfra.get("/ready")
async def infra_ready(handler: InfraHealthHandler = Depends(get_infra_health_handler)):
    result = await handler.readiness()
    return JSONResponse(status_code=200 if result["ok"] else 503, content=result)


@routerInfra.post("/events/users/doctor-created")
async def handle_user_service_doctor_created(
    payload: InfraEventRequest,
    handler: UserServiceDoctorCreatedHandler = Depends(get_user_service_doctor_created_handler),
):
    return await handler.handle(payload.to_payload())


@routerInfra.post("/events/users/patient-created")
async def handle_user_service_patient_created(
    payload: InfraEventRequest,
    handler: UserServicePatientCreatedHandler = Depends(get_user_service_patient_created_handler),
):
    return await handler.handle(payload.to_payload())


@routerInfra.post("/events/users/doctor-deleted")
async def handle_user_service_doctor_deleted(
    payload: InfraEventRequest,
    handler: UserServiceDoctorDeletedHandler = Depends(get_user_service_doctor_deleted_handler),
):
    return await handler.handle(payload.to_payload())


@routerInfra.post("/events/users/patient-deleted")
async def handle_user_service_patient_deleted(
    payload: InfraEventRequest,
    handler: UserServicePatientDeletedHandler = Depends(get_user_service_patient_deleted_handler),
):
    return await handler.handle(payload.to_payload())
