from .connectManager import ConnectionManager


#intermediario tradutor entre controller e a logica de websocket


class WebSocketGateway:

    def __init__(self, manager: ConnectionManager):
        self.manager = manager

    async def notify_appointment_scheduled(
        self,
        appointment_id: str
    ):

        await self.manager.broadcast({
            "event": "appointment_scheduled",
            "appointment_id": appointment_id
        })
        
    async def notify_day_loted(
        self,
        day: str
    ):

        await self.manager.broadcast({
            "event": "day_loted",
            "day": day
        })
        
    