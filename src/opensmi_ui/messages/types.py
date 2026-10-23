import uuid
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, computed_field

from opensmi_ui.model.json import JsonBaseModel, JsonOutModel


class WebSocketMessage(BaseModel):
    channel: str
    data: Any


class WebSocketMessageBatch(BaseModel):
    channel: str
    data: list[WebSocketMessage]


class Channel(StrEnum):
    """Usable channels for message. Note, that 'batch' is also a channel, reserved for batches with messages of these channels"""
    SERVER = "Server"
    MODEL = "Model"
    NOTIFICATION = "Notification"
    PIN_GUARD = "PinGuard"


class ChanneledMessage(JsonOutModel):
    channel: Channel
    data: JsonBaseModel | JsonOutModel


class SimpleUpdateMessage[T](JsonOutModel):
    update_content: T

    @computed_field
    @property
    def update_type(self) -> str:
        return self.update_content.__class__.__name__


class ModelUpdateMessage[T](JsonOutModel):
    entity_id: uuid.UUID | None

    update_content: T

    @computed_field
    @property
    def update_type(self) -> str:
        return self.update_content.__class__.__name__
