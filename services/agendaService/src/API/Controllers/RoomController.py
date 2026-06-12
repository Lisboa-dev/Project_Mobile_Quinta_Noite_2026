from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import require_admin
from src.api.provider import (
    get_create_room_use_case,
    get_delete_room_use_case,
    get_list_rooms_admin_detailed_query_use_case,
    get_list_rooms_query_use_case,
    get_room_admin_detail_query_use_case,
    get_room_by_id_query_use_case,
    get_update_room_use_case,
)
from src.api.interfaces.room import CreateRoomRequest, UpdateRoomRequest
from src.modules.agenda.aplication.dtos.useCase.query import GetByIdQuery, ListQuery


routerRoom = APIRouter(prefix="/rooms", tags=["Rooms"], dependencies=[Depends(require_admin)])


@routerRoom.post("/", status_code=status.HTTP_201_CREATED)
async def create_room(request: CreateRoomRequest, use_case=Depends(get_create_room_use_case)):
    result = await use_case.execute(request.name, triggered_by_id=request.triggered_by_id)
    return {"created": result}


@routerRoom.get("/admin/")
async def list_rooms_admin_detailed(
    limit: int | None = None,
    offset: int = 0,
    use_case=Depends(get_list_rooms_admin_detailed_query_use_case),
):
    return await use_case.execute(ListQuery(limit=limit, offset=offset))


@routerRoom.get("/admin/{room_id}")
async def get_room_admin_detail(
    room_id: str,
    use_case=Depends(get_room_admin_detail_query_use_case),
):
    room = await use_case.execute(GetByIdQuery(id=room_id))
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@routerRoom.get("/{room_id}")
async def get_room(room_id: str, use_case=Depends(get_room_by_id_query_use_case)):
    room = await use_case.execute(GetByIdQuery(id=room_id))
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@routerRoom.get("/")
async def list_rooms(
    limit: int | None = None,
    offset: int = 0,
    use_case=Depends(get_list_rooms_query_use_case),
):
    return await use_case.execute(ListQuery(limit=limit, offset=offset))


@routerRoom.put("/{room_id}")
async def update_room(
    room_id: str,
    request: UpdateRoomRequest,
    use_case=Depends(get_update_room_use_case),
):
    await use_case.execute(request.to_command(room_id))
    return {"updated": True}


@routerRoom.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: str, use_case=Depends(get_delete_room_use_case)):
    await use_case.execute(room_id)
