import asyncio
from asyncio import Task
from datetime import timedelta

from opensmi_ui.logger import get_module_logger

logger = get_module_logger("metrics")


class Metrics:
    def __init__(self, tick_delay: timedelta | None = None):
        if not tick_delay:
            tick_delay = timedelta(seconds=60)
        self._tick_delay = tick_delay
        self._tick_seconds = self._tick_delay.total_seconds()

        self._message_stats: dict[str, int] = {}
        self._serializer_stats: dict[str, int] = {}

        self._stats_task: Task | None = None

    async def start(self):
        if self._stats_task is not None and not self._stats_task.done():
            return

        logger.info("Metrics: Starting Task")
        self._stats_task = asyncio.create_task(self.print_stats())

    async def close(self):
        if self._stats_task is None:
            return

        logger.info("Metrics: Stopping Task")
        self._stats_task.cancel()

        try:
            await self._stats_task
        except asyncio.CancelledError:
            pass
        finally:
            self._stats_task = None

    def add_message_tick(self, msg_type: str):
        self._message_stats[msg_type] = self._message_stats.get(msg_type, 0) + 1

    def add_serialization_tick(self, value_type: str):
        self._serializer_stats[value_type] = (
            self._serializer_stats.get(value_type, 0) + 1
        )

    async def print_stats(self):
        try:
            while True:
                await asyncio.sleep(self._tick_seconds)

                if len(self._message_stats) == 0 and len(self._serializer_stats) == 0:
                    continue

                logger.info(f"Update Statistics (last {self._tick_seconds} seconds):")
                logger.info(self._message_stats)
                logger.info(self._serializer_stats)

                self._message_stats.clear()
                self._serializer_stats.clear()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception(
                "Metrics: An unhandeled exception stopped the print_Stats task!"
            )
            raise
