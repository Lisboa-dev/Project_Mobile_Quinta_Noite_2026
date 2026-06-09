from fastapi import APIRouter, Depends, Response, status

from src.api.ApiSchemas import ErrorResponse, MedicCreateRequest, UseCaseResponse, UserResponse
from src.api.ControllerUtils import dto_to_response, handle_domain_exception
from src.api.provider import UserFactory
from src.modules.users.application.dtos.useCase.command import CreateMedicCommand, DepreciatUserCommand, PromoteUserCommand


routerAdmins = APIRouter(prefix="/admins", tags=["admins"])


@routerAdmins.get("/", response_model=list[UserResponse])
async def list_admins(use_case=Depends(UserFactory.list_admin_use_case)):
    return [dto_to_response(item) for item in await use_case.execute()]


@routerAdmins.get("/{user_id}", response_model=UserResponse, responses={404: {"model": ErrorResponse}})
async def detail_admin(user_id: int, use_case=Depends(UserFactory.detail_admin_use_case)):
    try:
        return dto_to_response(await use_case.execute(user_id))
    except Exception as exc:
        handle_domain_exception(exc)


@routerAdmins.post("/{user_id}/promote", response_model=UseCaseResponse, responses={404: {"model": ErrorResponse}})
async def promote_user_to_admin(user_id: int, use_case=Depends(UserFactory.create_admin_use_case)):
    try:
        return dto_to_response(await use_case.execute(PromoteUserCommand(id=user_id)))
    except Exception as exc:
        handle_domain_exception(exc)


@routerAdmins.post("/doctors", response_model=UseCaseResponse, status_code=status.HTTP_201_CREATED, responses={409: {"model": ErrorResponse}})
async def admin_create_doctor(data: MedicCreateRequest, use_case=Depends(UserFactory.create_medic_use_case)):
    try:
        command = CreateMedicCommand(**data.model_dump())
        return dto_to_response(await use_case.execute(command))
    except Exception as exc:
        handle_domain_exception(exc)


@routerAdmins.post("/{user_id}/depreciate", response_model=UseCaseResponse, responses={404: {"model": ErrorResponse}})
async def depreciate_admin(user_id: int, use_case=Depends(UserFactory.delete_admin_use_case)):
    try:
        return dto_to_response(await use_case.execute(DepreciatUserCommand(id=user_id)))
    except Exception as exc:
        handle_domain_exception(exc)


@routerAdmins.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, responses={404: {"model": ErrorResponse}})
async def delete_admin(user_id: int, use_case=Depends(UserFactory.delete_admin_use_case)):
    try:
        await use_case.execute(DepreciatUserCommand(id=user_id))
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        handle_domain_exception(exc)
