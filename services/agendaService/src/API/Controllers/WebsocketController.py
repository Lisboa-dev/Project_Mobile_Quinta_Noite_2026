from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from src.api.provider import get_connection_manager


router = APIRouter(tags=["Websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, manager=Depends(get_connection_manager)):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
