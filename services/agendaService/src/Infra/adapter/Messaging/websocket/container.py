

#um provider singleton, ta aqui pois preciso dele nos consumers

from .gatewayWSImplement import (
    WebSocketGateway
)
from .connectManager import ConnectionManager

connection_manager = ConnectionManager()

#isso aqui será usado nos consumers para enviar eventos
websocket_gateway = WebSocketGateway(
    connection_manager
)