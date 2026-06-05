from fastapi import APIRouter, Depends, Response, status

from src.api.ApiSchemas import ErrorResponse, UserCreateRequest, UserResponse, UserUpdateRequest
from src.api.ControllerUtils import dto_to_response, handle_domain_exception
from src.api.Provider import UserFactory


routerAtendents = APIRouter(prefix="/atendents", tags=["atendents"])


@routerAtendents.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, responses={409: {"model": ErrorResponse}})
def create_atendent(data: UserCreateRequest, use_case=Depends(UserFactory.create_atendent_use_case)):
    try:
        return dto_to_response(use_case.execute(data))
    except Exception as exc:
        handle_domain_exception(exc)


@routerAtendents.get("/", response_model=list[UserResponse])
def list_atendents(use_case=Depends(UserFactory.list_atendent_use_case)):
    return [dto_to_response(item) for item in use_case.execute()]


@routerAtendents.get("/{user_id}", response_model=UserResponse, responses={404: {"model": ErrorResponse}})
def detail_atendent(user_id: int, use_case=Depends(UserFactory.detail_atendent_use_case)):
    try:
        return dto_to_response(use_case.execute(user_id))
    except Exception as exc:
        handle_domain_exception(exc)


@routerAtendents.put("/{user_id}", response_model=UserResponse, responses={404: {"model": ErrorResponse}})
def update_atendent(user_id: int, data: UserUpdateRequest, use_case=Depends(UserFactory.update_atendent_use_case)):
    try:
        payload = data.model_dump(exclude_unset=True)
        payload["id"] = user_id
        return dto_to_response(use_case.execute(payload))
    except Exception as exc:
        handle_domain_exception(exc)


@routerAtendents.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, responses={404: {"model": ErrorResponse}})
def delete_atendent(user_id: int, use_case=Depends(UserFactory.delete_atendent_use_case)):
    try:
        use_case.execute(user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        handle_domain_exception(exc)
