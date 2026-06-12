from fastapi import APIRouter, Depends, HTTPException, status

from src.api.provider import (
    get_create_doctor_use_case,
    get_delete_doctor_use_case,
    get_doctor_by_id_query_use_case,
    get_list_doctors_query_use_case,
    get_update_doctor_use_case,
)
from src.api.interfaces.doctor import CreateDoctorRequest, UpdateDoctorRequest
from src.modules.agenda.aplication.dtos.useCase.query import GetByIdQuery, ListQuery


routerDoctor = APIRouter(prefix="/doctors", tags=["Doctors"])


@routerDoctor.post("/", status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_doctor(request: CreateDoctorRequest, use_case=Depends(get_create_doctor_use_case)):
    result = await use_case.execute(request.to_command())
    return {"created": result}


@routerDoctor.get("/{doctor_id}")
async def get_doctor(doctor_id: str, use_case=Depends(get_doctor_by_id_query_use_case)):
    doctor = await use_case.execute(GetByIdQuery(id=doctor_id))
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@routerDoctor.get("/")
async def list_doctors(
    limit: int | None = None,
    offset: int = 0,
    use_case=Depends(get_list_doctors_query_use_case),
):
    return await use_case.execute(ListQuery(limit=limit, offset=offset))


@routerDoctor.put("/{doctor_id}")
async def update_doctor(
    doctor_id: str,
    request: UpdateDoctorRequest,
    use_case=Depends(get_update_doctor_use_case),
):
    await use_case.execute(request.to_command(doctor_id))
    return {"updated": True}


@routerDoctor.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(doctor_id: str, use_case=Depends(get_delete_doctor_use_case)):
    await use_case.execute(doctor_id)
