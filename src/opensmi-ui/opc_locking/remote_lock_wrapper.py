from datetime import datetime
from typing import Any

from pyuaadapter.client.base_remote_lock import BaseRemoteLock, RemoteLockSubscriber

from opc_locking.remote_lock_interface import RemoteLockInterface


class RemoteLockWrapper(RemoteLockInterface):
    """Wrapper for BaseRemoteLock"""

    remote_lock: BaseRemoteLock

    def __init__(self, base_remote_lock: BaseRemoteLock):
        self.remote_lock = base_remote_lock

    @property
    def locked(self) -> bool:
        return self.remote_lock.locked

    @property
    def locking_user(self) -> str:
        return self.remote_lock.locking_user

    @property
    def locking_client(self) -> str:
        return self.remote_lock.locking_client

    @property
    def locked_since(self) -> datetime | None:
        return self.remote_lock.locked_since

    def dto(self) -> dict[str, Any]:
        return self.remote_lock.dto()

    def add_subscriber(self, subscriber: RemoteLockSubscriber) -> None:
        return self.remote_lock.add_subscriber(subscriber)

    async def init_lock(self) -> None:
        return await self.remote_lock.init_lock()

    async def break_lock(self) -> None:
        return await self.remote_lock.break_lock()

    async def exit_lock(self) -> None:
        return await self.remote_lock.exit_lock()

    async def renew_lock(self) -> None:
        return await self.remote_lock.renew_lock()
