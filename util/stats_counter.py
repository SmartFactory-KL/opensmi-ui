import asyncio
import logging
from asyncio import Task

logger = logging.getLogger("uvicorn")

STATS_COUNTER_LOG_DELAY_SECONDS = 60.0


class StatsCounter:
    _self = None

    message_stats = {}
    serializer_stats = {}

    stats_task: Task | None = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self):
        pass

    def start_stats_counter_task(self):
        self.stats_task = asyncio.create_task(self.print_stats())

    def stop_stats_counter_task(self):
        if self.stats_task is not None:
            self.stats_task.cancel()

    def add_message_tick(self, msg_type: str):
        self.message_stats[msg_type] = self.message_stats.get(msg_type, 0) + 1

    def add_serialization_tick(self, value_type: str):
        self.serializer_stats[value_type] = self.serializer_stats.get(value_type, 0) + 1

    async def print_stats(self):
        try:
            while True:
                logger.info(
                    f"Update Statistics (last {STATS_COUNTER_LOG_DELAY_SECONDS} seconds):"
                )
                logger.info(self.message_stats)
                logger.info(self.serializer_stats)

                self.message_stats.clear()
                self.serializer_stats.clear()

                await asyncio.sleep(STATS_COUNTER_LOG_DELAY_SECONDS)
        except Exception as _:
            pass
