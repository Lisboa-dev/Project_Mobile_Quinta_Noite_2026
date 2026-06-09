from fastapi import APIRouter, Depends, HTTPException, status

from src.api.provider import (
    get_appointment_by_id_query_use_case,
    get_create_appointment_use_case,
    get_delete_appointment_use_case,
    get_list_appointments_query_use_case,
    get_update_appointment_use_case,
)
from src.api.interfaces.appointment import (
    CreateAppointmentRequest,
    DeleteAppointmentRequest,
    UpdateAppointmentRequest,
)
from src.modules.agenda.aplication.dtos.useCase.query import GetByIdQuery, ListQuery


routerAppointment = APIRouter(prefix="/appointments", tags=["Appointments"])


@routerAppointment.post("/", status_code=status.HTTP_201_CREATED)
async def create_appointment(
    request: CreateAppointmentRequest,
    use_case=Depends(get_create_appointment_use_case),
):
    command = request.to_command()
    result = await use_case.execute(command)
    if not result:
        raise HTTPException(status_code=400, detail="Appointment could not be created")
    return {"created": True}


@routerAppointment.get("/{appointment_id}")
async def get_appointment(
    appointment_id: str,
    use_case=Depends(get_appointment_by_id_query_use_case),
):
    appointment = await use_case.execute(GetByIdQuery(id=appointment_id))
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@routerAppointment.get("/")
async def list_appointments(
    limit: int | None = None,
    offset: int = 0,
    use_case=Depends(get_list_appointments_query_use_case),
):
    return await use_case.execute(ListQuery(limit=limit, offset=offset))


@routerAppointment.put("/{appointment_id}")
async def update_appointment(
    appointment_id: str,
    request: UpdateAppointmentRequest,
    use_case=Depends(get_update_appointment_use_case),
):
    command = request.to_command(appointment_id)
    result = await use_case.execute(command)
    if not result:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"updated": True}


@routerAppointment.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: str,
    use_case=Depends(get_delete_appointment_use_case),
):
    await use_case.execute(DeleteAppointmentRequest().to_command(appointment_id))
