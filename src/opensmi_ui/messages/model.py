from typing import Any

from pydantic import BaseModel


class WebSocketMessage(BaseModel):
    channel: str
    data: Any


class WebSocketMessageBatch(BaseModel):
    channel: str
    data: list[WebSocketMessage]
