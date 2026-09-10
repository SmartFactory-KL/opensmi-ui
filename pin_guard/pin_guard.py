import asyncio
import datetime
import logging
import uuid

from messages.message_funnel import MessageFunnel
from model.pin_guard_types import (
    PinGuardState,
    PinGuardStateUpdate,
    PinGuardUnlockRequest,
    PinGuardUpdateMessage,
)

logger = logging.getLogger("uvicorn")

msg_funnel = MessageFunnel()


class PinGuard:
    pin: str = "123456"

    entity_id: uuid.UUID

    autolock_timedelta: datetime.timedelta
    autolock_timestamp: datetime.datetime

    is_enabled: bool
    is_locked: bool

    autolock_task: asyncio.Task

    def __init__(self, is_enabled: bool, pin: str, autolock_delay: int):
        self.pin = pin

        self.entity_id = uuid.uuid4()

        self.autolock_timedelta = datetime.timedelta(seconds=autolock_delay)
        self.autolock_timestamp = datetime.datetime.now()

        self.is_enabled = is_enabled
        self.is_locked = True

        self.autolock_task = asyncio.create_task(self.check_auto_lock())

    def check(self):
        """This returns true, if the PinGuard is in a state that allows actions to happen"""
        if not self.is_enabled:
            return True

        if not self.is_locked:
            return True

        return False

    def request_unlock_with_pin(self, pin_input: PinGuardUnlockRequest):
        if self.pin == pin_input.pin:
            self._unlock()
        else:
            raise ValueError("Pin Guard: Incorrect PIN")

    def request_lock(self):
        if not self.is_locked:
            self._lock()

    def _lock(self):
        self.is_locked = True
        self.broadcast_pin_state()
        logger.info("Pin Guard: Locked")

    def _unlock(self):
        self.is_locked = False
        self.autolock_timestamp = datetime.datetime.now()
        self.broadcast_pin_state()
        logger.info("Pin Guard: Unlocked")

    def unlock_for_shutdown(self):
        """Only to be used for server lifecycle to prevent exceptions on shutdown or Ctrl + C"""
        self._unlock()

    def get_state(self) -> PinGuardState:
        return PinGuardState(is_locked=self.is_locked, is_enabled=self.is_enabled)

    def broadcast_pin_state(self):
        msg = PinGuardUpdateMessage[PinGuardStateUpdate](
            entity_id=self.entity_id,
            update_content=PinGuardStateUpdate(new_is_locked=self.is_locked),
        )
        msg_funnel.send_direct_message(msg)

    def tick_auto_lock(self):
        self.autolock_timestamp = datetime.datetime.now()

    async def check_auto_lock(self):
        if not self.is_enabled:
            logger.info("Pin Guard is not enabled. No check_auto_lock.")
            return

        try:
            logger.info("Pin Guard: Starting check_auto_lock")
            while True:
                if self.is_locked is False:
                    if datetime.datetime.now() > (
                        self.autolock_timestamp + self.autolock_timedelta
                    ):
                        logger.info("Pin Guard: Automatically locked")
                        self._lock()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Pin Guard: Cancelled check_auto_lock")
            raise
        except Exception as e:
            logger.error(e)
