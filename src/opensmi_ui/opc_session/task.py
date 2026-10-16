import asyncio
from collections.abc import Callable, Coroutine
from typing import Any


class StoppableTask:
    def __init__(self, worker: Callable[[asyncio.Event], Coroutine[Any, Any, None]]):
        self._lock = asyncio.Lock()
        self._worker = worker

        self._task: asyncio.Task[None] | None = None
        self._stop_event: asyncio.Event | None = None

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self):
        async with self._lock:
            if self._task is not None:
                await self._stop_locked()

            self._stop_event = asyncio.Event()
            self._task = asyncio.create_task(self._worker(self._stop_event))

    async def stop(self):
        async with self._lock:
            await self._stop_locked()

    async def _stop_locked(self) -> None:
        if self._task is None:
            return

        if not self._task.done() and self._stop_event is not None:
            self._stop_event.set()

        try:
            # Wait for the worker to finish its cleanup.
            await self._task
        finally:
            self._task = None
            self._stop_event = None


async def wait_or_stop[T](
    awaitable: Coroutine[Any, Any, T],
    stop_event: asyncio.Event,
) -> T | None:
    operation = asyncio.create_task(awaitable)
    stopping = asyncio.create_task(stop_event.wait())

    try:
        done, _ = await asyncio.wait(
            {operation, stopping},
            return_when=asyncio.FIRST_COMPLETED,
        )

        if stopping in done:
            return None

        return operation.result()

    finally:
        for task in (operation, stopping):
            if not task.done():
                task.cancel()

        await asyncio.gather(
            operation, stopping, return_exceptions=True
        )
