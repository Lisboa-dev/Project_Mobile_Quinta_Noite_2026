from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.infra.websocket import events_hub, notifications_hub

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/events")
async def websocket_events(websocket: WebSocket) -> None:
    await events_hub.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        events_hub.disconnect(websocket)


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket) -> None:
    await notifications_hub.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        notifications_hub.disconnect(websocket)
