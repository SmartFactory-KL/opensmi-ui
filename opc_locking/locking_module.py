import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from uuid import UUID

from pydantic import BaseModel
from pyuaadapter.client.base_remote_lock import BaseRemoteLock, RemoteLockSubscriber
from pyuaadapter.client.remote_server import RemoteServer

import app_config
from messages.message_funnel import MessageFunnel
from model.machine_types import (
    MachineLockStateUpdate,
    MachineLockUserUpdate,
    MachineUpdateMessage,
)
from model.node_types import LockingModuleDto
from opc_locking.locking_simulation import LockingSimulation
from opc_locking.remote_lock_interface import RemoteLockInterface
from opc_locking.remote_lock_wrapper import RemoteLockWrapper

logger = logging.getLogger("uvicorn")

msg_funnel = MessageFunnel()


class LockingConfiguration(BaseModel):
    is_enabled: bool
    is_simulated: bool
    autofree_delay_seconds: int
    locking_simulation_username: str


class LockingModule(RemoteLockSubscriber):
    remote_lock: RemoteLockInterface
    machine_entity_id: uuid.UUID
    parent_server: RemoteServer

    lock_config: LockingConfiguration

    auto_free_task: asyncio.Task
    auto_free_timestamp: datetime
    auto_free_delay: timedelta

    def __init__(
        self,
        remote_lock: BaseRemoteLock | None,
        machine_entity_id: UUID,
        lock_config: LockingConfiguration,
        parent_server: RemoteServer,
    ):
        self.lock_config = lock_config

        self.remote_lock = LockingSimulation(lock_config.locking_simulation_username)
        if not self.lock_config.is_simulated and remote_lock is not None:
            self.remote_lock = RemoteLockWrapper(remote_lock)

        self.machine_entity_id = machine_entity_id
        self.parent_server = parent_server

        self.auto_free_timestamp = datetime.now()
        self.auto_free_timedelta = timedelta(
            seconds=app_config.get_int("LOCKING_AUTOFREE_DELAY_SECONDS")
        )

        self.remote_lock.add_subscriber(self)
        self.auto_free_task = asyncio.create_task(self._check_for_auto_free())

    def to_dto(self) -> LockingModuleDto:
        result = LockingModuleDto(
            is_enabled=self.lock_config.is_enabled,
            is_locked=self.remote_lock.locked,
            is_locked_since=(
                self.remote_lock.locked_since.isoformat()
                if self.remote_lock.locked_since is not None
                else ""
            ),
            is_simulated=self.lock_config.is_simulated,
            locking_client=self.remote_lock.locking_client,
            locking_user=self.remote_lock.locking_user,
        )

        return result

    ## Basic functions
    async def request_lock_toggle(self):
        self.check_if_locking_enabled()
        logger.info("Requesting Lock Operation: Toggle")

        if self.remote_lock.locked:
            await self.remote_lock.exit_lock()
        else:
            await self.remote_lock.init_lock()
            self.tick_auto_free_task()

    async def request_lock_exit(self):
        self.check_if_locking_enabled()
        logger.info("Requesting Lock Operation: Exit")

        if self.remote_lock.locked:
            await self.remote_lock.exit_lock()

    async def request_lock_break(self):
        self.check_if_locking_enabled()
        logger.info("Requesting Lock Operation: Break")

        if self.remote_lock.locked:
            await self.remote_lock.break_lock()
            self.tick_auto_free_task()

    def check_if_locking_enabled(self):
        if self.lock_config.is_enabled is not True:
            raise Exception(
                "Locking is disabled but a Lock Action was requested. Aborted."
            )

    def is_locking_enabled(self):
        return self.lock_config.is_enabled

    ## Auto Free
    def tick_auto_free_task(self):
        """Resets the timestamp for the auto_free task to the current time"""
        self.auto_free_timestamp = datetime.now()

    def cancel_auto_free_task(self):
        """Send cancel() to the auto_free task"""
        self.auto_free_task.cancel()

    async def _check_for_auto_free(self):
        try:
            logger.info(
                f"Starting auto unlock task on machine {self.machine_entity_id}"
            )
            while True:
                # check the lock itself
                if (
                    self.remote_lock.locked
                    and self.remote_lock.locking_user == self.parent_server.username
                ):
                    if datetime.now() > (
                        self.auto_free_timestamp + self.auto_free_timedelta
                    ):
                        logger.info("LockingModule: Auto free triggered")
                        try:
                            await self.request_lock_exit()
                            self.is_pin_unlocked = False
                        except Exception as _:
                            logger.info("unable to exit lock")

                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info(
                f"Stopping auto unlock task on machine {self.machine_entity_id}"
            )
            raise
        except Exception as e:
            logger.warning("auto free task has exception")
            logger.warning(e)

    ## Server Lifecycle
    def on_server_disconnect(self):
        self.cancel_auto_free_task()

    ## Subscriber methods
    def on_locked_state_changed(self, new_state):
        msg = MachineUpdateMessage[MachineLockStateUpdate](
            entity_id=self.machine_entity_id,
            update_content=MachineLockStateUpdate(is_locked=new_state),
        )
        msg_funnel.send_direct_message(msg)

    def on_locking_user_changed(self, new_locking_user):
        msg = MachineUpdateMessage[MachineLockUserUpdate](
            entity_id=self.machine_entity_id,
            update_content=MachineLockUserUpdate(new_locking_user=new_locking_user),
        )
        msg_funnel.send_direct_message(msg)
