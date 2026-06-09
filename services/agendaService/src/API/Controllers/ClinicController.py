from fastapi import APIRouter, Depends, HTTPException, status

from src.api.provider import (
    get_clinic_by_id_query_use_case,
    get_create_clinic_use_case,
    get_delete_clinic_use_case,
    get_list_clinics_query_use_case,
    get_clinic_repository,
)
from src.api.interfaces.clinic import CreateClinicRequest, UpdateClinicRequest
from src.modules.agenda.aplication.dtos.useCase.query import GetByIdQuery, ListQuery


routerClinic = APIRouter(prefix="/clinics", tags=["Clinics"])


@routerClinic.post("/", status_code=status.HTTP_201_CREATED)
async def create_clinic(request: CreateClinicRequest, use_case=Depends(get_create_clinic_use_case)):
    result = await use_case.execute(request.to_command())
    return {"created": result}


@routerClinic.get("/{clinic_id}")
async def get_clinic(clinic_id: str, use_case=Depends(get_clinic_by_id_query_use_case)):
    clinic = await use_case.execute(GetByIdQuery(id=clinic_id))
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic


@routerClinic.get("/")
async def list_clinics(
    limit: int | None = None,
    offset: int = 0,
    use_case=Depends(get_list_clinics_query_use_case),
):
    return await use_case.execute(ListQuery(limit=limit, offset=offset))


@routerClinic.put("/{clinic_id}")
async def update_clinic(
    clinic_id: str,
    request: UpdateClinicRequest,
    repository=Depends(get_clinic_repository),
    query_use_case=Depends(get_clinic_by_id_query_use_case),
):
    clinic = await query_use_case.execute(GetByIdQuery(id=clinic_id))
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    await repository.update(request.to_command(clinic_id))
    return {"updated": True}


@routerClinic.delete("/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clinic(clinic_id: str, use_case=Depends(get_delete_clinic_use_case)):
    await use_case.execute(clinic_id)
