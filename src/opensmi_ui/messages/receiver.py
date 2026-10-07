from dataclasses import dataclass
from datetime import UTC, datetime

from asyncua.ua import Variant
from opensmi.client import (
    BaseRemoteComponent,
    NotificationEvent,
    RemoteLock,
    RemoteServerStatus,
    RemoteSkill,
    RemoteUser,
    RemoteVariable,
)
from opensmi.core import SkillState

from opensmi_ui.logger import get_module_logger
from opensmi_ui.messages.funnel import MessageFunnel
from opensmi_ui.model.common import GenericUpdateEntityType, GenericUpdateMessage

logger = get_module_logger("messages.receiver")


@dataclass(frozen=True)
class ServerStateUpdate:
    new_state: str


@dataclass(frozen=True)
class ServerTimeUpdate:
    new_time: str


class MessageReceiver:
    def __init__(self, funnel: MessageFunnel):
        self.funnel = funnel

    # server channel
    async def receive_server_state(self, new_state: RemoteServerStatus) -> None:
        msg = GenericUpdateMessage[ServerStateUpdate](
            entity_id=None,
            entity_type=GenericUpdateEntityType.Server,
            update_content=ServerStateUpdate(new_state=new_state.name),
        )

        self.funnel.send_direct_message(msg)

    async def receive_server_time(self, new_time: datetime) -> None:
        msg = GenericUpdateMessage[ServerTimeUpdate](
            entity_id=None,
            entity_type=GenericUpdateEntityType.Server,
            update_content=ServerTimeUpdate(
                new_time=new_time.astimezone(UTC).isoformat()
            ),
        )

        self.funnel.send_direct_message(msg)

    # model channel
    async def receive_component_state(
        self, component: BaseRemoteComponent, new_state: str
    ) -> None:
        logger.info(new_state)

    async def receive_component_notification(
        self, component: BaseRemoteComponent, notification: NotificationEvent
    ) -> None:
        logger.info(notification)

    async def receive_skill_state(
        self, skill: RemoteSkill, new_state: SkillState
    ) -> None:
        logger.info(new_state)

    async def receive_lock_changed(self, lock: RemoteLock, new_is_locked: bool) -> None:
        logger.info(new_is_locked)
        logger.info(lock.parent.name)

    async def receive_lock_user_changed(
        self, lock: RemoteLock, new_username: str
    ) -> None:
        logger.info(new_username)

    async def receive_user_presence_changed(
        self, user: RemoteUser, new_user_presence: bool
    ) -> None:
        logger.info(new_user_presence)

    async def receive_value_changed(
        self, variable: RemoteVariable, new_value: Variant
    ) -> None:
        # logger.info(new_value)
        ...
