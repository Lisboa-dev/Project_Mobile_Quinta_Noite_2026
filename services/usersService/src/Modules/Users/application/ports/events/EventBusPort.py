from typing import Protocol


class EventBusPort(Protocol):
    def publish(self, event) -> None: ...




