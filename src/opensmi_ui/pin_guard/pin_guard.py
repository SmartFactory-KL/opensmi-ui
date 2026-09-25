import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta
from time import monotonic

from opensmi_ui.model.common import (
    GenericUpdateEntityType,
    GenericUpdateMessage,
    JsonBaseModel,
    JsonOutModel,
)

logger = logging.getLogger("uvicorn.opensmi_ui.pin_guard")


@dataclass
class PinGuardConfig:
    is_enabled: bool = False
    # pin is a str here but int in config to prevent non-digit pins but have easier comparison
    pin: str = "123456"
    autolock_delay: timedelta = timedelta(seconds=60)


class PinGuardState(JsonOutModel):
    is_locked: bool
    is_enabled: bool


class PinGuardUnlockRequest(JsonBaseModel):
    pin: str


class PinGuardUpdateMessage[T](GenericUpdateMessage[T]):
    entity_type: GenericUpdateEntityType = GenericUpdateEntityType.PinGuard


class PinGuardStateUpdate(JsonOutModel):
    is_locked: bool


class PinGuard:
    def __init__(self, cfg: PinGuardConfig | None = None):
        if not cfg:
            cfg = PinGuardConfig()

        self._pin = cfg.pin

        self._autolock_timedelta_seconds = cfg.autolock_delay.total_seconds()
        self._autolock_deadline = monotonic() + self._autolock_timedelta_seconds

        self._is_enabled = cfg.is_enabled

        # if the guard is not enabled, it should never be locked
        self._is_locked = cfg.is_enabled

        self._autolock_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        if not self._is_enabled:
            return

        if self._autolock_task is not None and not self._autolock_task.done():
            return

        logger.info("PinGuard: Starting AutoLock Task")
        self.tick_auto_lock()
        self._autolock_task = asyncio.create_task(self.check_auto_lock())

    async def close(self) -> None:
        if not self._is_enabled:
            return

        if self._autolock_task is None:
            return

        logger.info("PinGuard: Stopping AutoLock Task")
        self._autolock_task.cancel()

        try:
            await self._autolock_task
        except asyncio.CancelledError:
            pass
        finally:
            self._autolock_task = None

    def locked(self):
        """Returns True if the PinGuard is locked and no action should happen. Returns False it the PinGuard is not enabled"""
        if not self._is_enabled:
            return False

        return self._is_locked

    def get_state(self) -> PinGuardState:
        return PinGuardState(is_locked=self.locked(), is_enabled=self._is_enabled)

    def request_unlock(self, pin_input: PinGuardUnlockRequest):
        if not self._is_enabled:
            return

        if self._pin == pin_input.pin:
            self._unlock()
        else:
            raise ValueError("Pin Guard: Incorrect PIN")

    def request_lock(self):
        if not self._is_enabled:
            return

        if not self._is_locked:
            self._lock()

    def _lock(self):
        self._is_locked = True
        logger.info("PinGuard: Locked")

    def _unlock(self):
        self._is_locked = False
        self.tick_auto_lock()
        logger.info("PinGuard: Unlocked")

    def tick_auto_lock(self):
        self._autolock_deadline = monotonic() + self._autolock_timedelta_seconds

    async def check_auto_lock(self):
        try:
            while True:
                if self._is_locked is False and monotonic() >= (
                    self._autolock_deadline
                ):
                    self._lock()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            raise
        except Exception:
            self._lock()
            logger.exception(
                "PinGuard: An unhandeled exception stopped the check_auto_lock task! This triggered a locking!"
            )
            raise
