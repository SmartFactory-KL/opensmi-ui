from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol, TypeGuard
from uuid import UUID

from asyncua.client.ua_client import UaClientState
from pydantic import BaseModel

from opensmi_ui.logger import get_module_logger
from opensmi_ui.messages.funnel import MessageFunnel
from opensmi_ui.messages.types import (
    Channel,
    ChanneledMessage,
    ModelUpdateMessage,
    SimpleUpdateMessage,
)
from opensmi_ui.model.json import JsonBaseModel, JsonOutModel

logger = get_module_logger("messages.receiver")


@dataclass(frozen=True)
class ServerStateUpdate:
    new_state: str


@dataclass(frozen=True)
class ServerTimeUpdate:
    new_time: str


class HasEntityId(Protocol):
    entity_id: UUID


def has_entity_id(
    model: BaseModel,
) -> TypeGuard[HasEntityId]:
    return "entity_id" in type(model).model_fields


class MessageReceiver:
    def __init__(self, funnel: MessageFunnel):
        self.funnel = funnel

    # server channel
    def receive_server_state(self, new_state: UaClientState) -> None:
        msg = ChanneledMessage(
            channel=Channel.SERVER,
            data=SimpleUpdateMessage[ServerStateUpdate](
                update_content=ServerStateUpdate(new_state=str(new_state.value))
            ),
        )

        self.funnel.send_direct_message(msg)

    def receive_server_time(self, new_time: datetime) -> None:
        msg = ChanneledMessage(
            channel=Channel.SERVER,
            data=SimpleUpdateMessage[ServerTimeUpdate](
                update_content=ServerTimeUpdate(
                    new_time=new_time.astimezone(UTC).isoformat()
                ),
            ),
        )

        self.funnel.send_direct_message(msg)

    def receive_event_bus_update(self, update: JsonBaseModel | JsonOutModel):
        if not has_entity_id(update):
            return

        msg = ChanneledMessage(
            channel=Channel.MODEL,
            data=ModelUpdateMessage[type(update)](
                entity_id=update.entity_id,
                update_content=update,
            ),
        )

        self.funnel.queue_message(msg)
