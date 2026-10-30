import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

from opensmi_ui.logger import get_module_logger

logger = get_module_logger("opc_session.stoppable_task")


class StoppableTask:
    def __init__(self, worker: Callable[[], Coroutine[Any, Any, None]]):
        self._lock = asyncio.Lock()
        self._worker = worker
        self._task: asyncio.Task[None] | None = None

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self) -> None:
        async with self._lock:
            await self._stop_locked()
            self._task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        async with self._lock:
            await self._stop_locked()

    async def _stop_locked(self) -> None:
        task, self._task = self._task, None
        if task is None:
            return

        task.cancel()
        # wait() neither raises the task's exception nor swallows *our* cancellation
        await asyncio.wait({task})

        if not task.cancelled() and (exc := task.exception()):
            logger.warning("Worker ended with an error: %r", exc)
