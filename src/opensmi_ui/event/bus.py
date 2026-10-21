from collections.abc import Callable

from opensmi_ui.model.json import JsonBaseModel, JsonOutModel

Handler = Callable[[JsonOutModel | JsonBaseModel], None]


class EventBus:
    def __init__(self):
        self._handlers: dict[str, Handler] = {}

    def subscribe(self, client_id: str, handler: Handler):
        self._handlers[client_id] = handler

    def unsubscribe(self, client_id):
        if client_id in self._handlers:
            self._handlers.pop(client_id)

    def publish(self, data: JsonOutModel | JsonBaseModel):
        for handler in self._handlers.values():
            handler(data)
