# infra/websocket/connection_manager.py

from fastapi import WebSocket

#controler de conexões e implementação real de broadcast

class ConnectionManager:

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):

        await websocket.accept()

        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):

        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):

        closed_connections: list[WebSocket] = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except RuntimeError:
                closed_connections.append(connection)

        for connection in closed_connections:
            self.disconnect(connection)
