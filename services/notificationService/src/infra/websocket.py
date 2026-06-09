from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder


class WebSocketHub:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast(self, payload: dict) -> None:
        closed: list[WebSocket] = []
        serializable_payload = jsonable_encoder(payload)
        for websocket in self._connections:
            try:
                await websocket.send_json(serializable_payload)
            except RuntimeError:
                closed.append(websocket)

        for websocket in closed:
            self.disconnect(websocket)

    def snapshot(self) -> dict[str, int]:
        return {"connections": len(self._connections)}


events_hub = WebSocketHub()
notifications_hub = WebSocketHub()

# Backward-compatible alias used by older controllers/tests.
hub = notifications_hub
