from typing import Any, Callable


class BusPort:
    def emit(self, event: Any, data: Any = None) -> Any:
        pass

    def publish(self, event: Any = None, data: Any = None) -> Any:
        return self.emit(event, data)

    def on(self, event: Any, callback: Callable[..., Any]) -> Any:
        pass
