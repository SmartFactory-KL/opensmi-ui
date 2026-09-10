from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pyuaadapter.client.base_remote_lock import RemoteLockSubscriber


class RemoteLockInterface(ABC):
    """Interface for remote lock management."""

    @property
    @abstractmethod
    def locked(self) -> bool:
        """True if module is locked, False otherwise."""
        pass

    @property
    @abstractmethod
    def locking_user(self) -> str:
        """Name of the locking user or empty string if unlocked."""
        pass

    @property
    @abstractmethod
    def locking_client(self) -> str:
        """Hostname of the locking client or empty string if unlocked."""
        pass

    @property
    @abstractmethod
    def locked_since(self) -> datetime | None:
        """Timestamp when the module was locked, or None if unlocked."""
        pass

    @abstractmethod
    def dto(self) -> dict[str, Any]:
        """Returns a dict representation of the lock state."""
        pass

    @abstractmethod
    def add_subscriber(self, subscriber: RemoteLockSubscriber) -> None:
        """Adds a subscriber to receive lock change notifications."""
        pass

    @abstractmethod
    async def init_lock(self) -> None:
        """Occupies the remote module; fails if already locked."""
        pass

    @abstractmethod
    async def break_lock(self) -> None:
        """Forces lock takeover; may fail if higher priority prevents it."""
        pass

    @abstractmethod
    async def exit_lock(self) -> None:
        """Releases the lock; fails if we are not the locking user."""
        pass

    @abstractmethod
    async def renew_lock(self) -> None:
        """Renews the lock; fails if we are not the locking user."""
        pass
