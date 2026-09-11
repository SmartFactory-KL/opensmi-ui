from __future__ import annotations

from datetime import datetime
from typing import List

from pyuaadapter.client.base_remote_lock import RemoteLockSubscriber

from model.machine_types import LockingState
from opc_locking.remote_lock_interface import RemoteLockInterface


class LockingSimulation(RemoteLockInterface):
    """Simulation of a RemoteLock"""

    _locking_user: str = ""
    _locking_client: str = "sim-lock-client"
    _locked: bool = False
    _locked_since: datetime | None = None

    _username_to_use: str = "sim-user"

    _subscribers: List[RemoteLockSubscriber]

    def __init__(self, locking_username: str):
        self._username_to_use = locking_username
        self._subscribers = []

    @property
    def locked(self) -> bool:
        """True if module is locked, False otherwise."""
        return self._locked

    @property
    def locking_user(self) -> str:
        """Name of the locking user or empty string if unlocked."""
        return self._locking_user

    @property
    def locking_client(self) -> str:
        """Hostname of the locking client or empty string if unlocked."""
        return self._locking_client

    @property
    def locked_since(self) -> datetime | None:
        """Timestamp when the module was locked, or None if unlocked."""
        return self._locked_since

    def dto(self) -> LockingState:
        """Returns a dict representation of the lock state."""
        locked_since_string = ""
        if self.locked_since is not None:
            locked_since_string = self.locked_since.isoformat()
        return {
            "locked": self.locked,
            "locking_user": self.locking_user,
            "locking_client": self.locking_client,
            "locked_since": locked_since_string,
        }

    def add_subscriber(self, subscriber: RemoteLockSubscriber) -> None:
        """Adds a subscriber to receive lock change notifications."""
        self._subscribers.append(subscriber)

    def _broadcast_state_to_subscribers(self):
        for sub in self._subscribers:
            sub.on_locked_state_changed(self.locked)
            sub.on_locking_user_changed(self.locking_user)

    async def init_lock(self) -> None:
        """Request the locking of this Lock"""
        if self._locked:
            raise Exception("Lock is already engaged")

        self._locked = True
        self._locking_user = self._username_to_use
        self._locked_since = datetime.now()
        self._broadcast_state_to_subscribers()

    async def break_lock(self) -> None:
        """Forces lock takeover; may fail if higher priority prevents it."""
        if not self.locked:
            raise Exception(
                "Breaking a lock is not allowed when it is not locked at the moment"
            )

        self._locked = True
        self._locking_user = self._username_to_use
        self._locked_since = datetime.now()
        self._broadcast_state_to_subscribers()

    async def exit_lock(self) -> None:
        """Releases the lock; fails if we are not the locking user."""
        self._locked = False
        self._locking_user = ""
        self._locked_since = None
        self._broadcast_state_to_subscribers()

    async def renew_lock(self) -> None:
        """Renews the lock; fails if we are not the locking user."""
        self.init_lock()
