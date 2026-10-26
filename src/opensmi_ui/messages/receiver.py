from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol, TypeGuard
from uuid import UUID

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
from opensmi_ui.opc_session.session import OPCSessionData
from opensmi_ui.opc_subscriber.notification import NotificationEvent

logger = get_module_logger("messages.receiver")


@dataclass(frozen=True)
class ServerSessionUpdate:
    new_session: OPCSessionData


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
    def receive_server_session(self, new_session: OPCSessionData) -> None:
        msg = ChanneledMessage(
            channel=Channel.SERVER,
            data=SimpleUpdateMessage[ServerSessionUpdate](
                update_content=ServerSessionUpdate(new_session=new_session)
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
        # handle notifications differently
        if isinstance(update, NotificationEvent):
            msg = ChanneledMessage(channel=Channel.NOTIFICATION, data=update)
        else:
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
