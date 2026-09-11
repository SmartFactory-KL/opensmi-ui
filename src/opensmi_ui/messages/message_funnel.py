import asyncio
import logging
import time

from messages.message_broadcaster import MessageBroadcaster, WebSocketMessage
from model.common_types import GenericUpdateMessage
from util.stats_counter import StatsCounter

MESSAGE_FUNNEL_BATCH_DELAY_SECONDS = 0.05


logger = logging.getLogger("uvicorn")
message_broadcaster = MessageBroadcaster()
stats_counter = StatsCounter()


class MessageFunnel:
    _self = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
            cls._self._initialized = False
        return cls._self

    def __init__(self):
        if self._initialized:
            return

        self._receiving_buffer: list[WebSocketMessage] = []
        self._sending_buffer: list[WebSocketMessage] = []

        self._is_active: bool = False
        self._batching_task: asyncio.Task
        self._batch_count: int = 0
        self._batch_tick_stats: list[float] = []

        self._batching_watchdog_task: asyncio.Task
        self._degraded_watchdog_count: int = 0

        self._initialized = True

    def send_direct_message(self, message: GenericUpdateMessage):
        """
        Directly send a message to all clients without batching.
        Only use this for critical messages like connection state
        or server time
        """
        stats_counter.add_message_tick(message.update_type)
        asyncio.create_task(
            message_broadcaster.broadcast(
                WebSocketMessage(channel=message.entity_type, data=message)
            )
        )

    def send_refresh_signal(self):
        """
        Directly send a special refresh message which asks the client
        to request all machine data again
        """
        stats_counter.add_message_tick("refresh")
        asyncio.create_task(
            message_broadcaster.broadcast(
                WebSocketMessage(channel="refresh", data=None)
            )
        )

    def queue_message(self, message: GenericUpdateMessage):
        """
        Append message to the current queue for the next batch
        """
        if not self._is_active:
            logger.debug("MessageFunnel: received message on inactive batching task!")
            return

        stats_counter.add_message_tick(message.update_type)
        web_socket_message = WebSocketMessage(channel=message.entity_type, data=message)
        self._receiving_buffer.append(web_socket_message)

    async def flush_messages(self):
        """
        Switch buffers and send all messages from last batch
        """

        tmp_buffer = self._receiving_buffer
        self._receiving_buffer = self._sending_buffer
        self._sending_buffer = tmp_buffer

        # send batch out
        if len(self._sending_buffer) > 0:
            await message_broadcaster.broadcast_batch(self._sending_buffer)

        # clear sending buffer to be used as next receiving buffer
        del self._sending_buffer[:]

    def enable_batching_task(self):
        """
        Enable both the batching task and its watchdog.
        The batching task flushes all messages to the message_broadcaster in ticks,
        The watchdog makes sure the task still runs in a healthy way
        """
        if self._is_active is True:
            return

        self._batch_count = 0
        self._degraded_watchdog_count = 0

        del self._batch_tick_stats[:]

        self._clear_buffers()

        self._is_active = True
        self._batching_task = asyncio.create_task(self._send_next_batch())
        self._batching_watchdog_task = asyncio.create_task(self._watch_batching())

    def disable_batching_task(self):
        if self._is_active is False:
            return

        self._is_active = False

        current_task = asyncio.current_task()
        for task in (self._batching_task, self._batching_watchdog_task):
            if task is not None and task is not current_task and not task.done():
                task.cancel()

        self._clear_buffers()

    def _clear_buffers(self):
        del self._receiving_buffer[:]
        del self._sending_buffer[:]

    async def _send_next_batch(self):
        interval = MESSAGE_FUNNEL_BATCH_DELAY_SECONDS
        next_tick = time.monotonic()

        try:
            while True:
                if self._is_active is False:
                    return

                next_tick += interval

                # send next batch
                await self.flush_messages()
                self._batch_count += 1

                sleep_delay = next_tick - time.monotonic()
                self._batch_tick_stats.append(sleep_delay)

                if sleep_delay > 0:
                    await asyncio.sleep(sleep_delay)
                else:
                    # sending messages took lonker than the tick
                    # so re-run loop with new next_tick
                    # and mark the longer runtime
                    next_tick = time.monotonic()

                # set delay for next batch -> actual delay might be more if
                # sending takes too long
        except asyncio.CancelledError as e:
            logger.info("message funnel batching has been canceled")
            raise e
        except Exception as e:
            logger.error(
                "MessageFunnel: batching task had an exception and will be disabled now"
            )
            logger.exception(e)

            # only cancel the watchdog as the batching task will return after this anyway.
            # keeps the current_task from cancelling itself.
            self._is_active = False
            if (
                self._batching_watchdog_task is not None
                and not self._batching_watchdog_task.done()
            ):
                self._batching_watchdog_task.cancel()

            self._clear_buffers()

            return

    async def _watch_batching(self):
        try:
            while True:
                # this delay is a multiple of the batch delay
                # as it might happen in high load situations that the sending takes
                # time without it being stuck
                await asyncio.sleep(20 * MESSAGE_FUNNEL_BATCH_DELAY_SECONDS)

                # check and reset the batch count.
                # a degraded task would not be able to keep up
                if self._batch_count < 3:
                    logger.warning(
                        "MessageFunnel: low batch count, batching might be degraded"
                    )
                    self._degraded_watchdog_count += 1
                else:
                    self._degraded_watchdog_count = 0

                # reset batch count
                self._batch_count = 0

                # check and reset stats
                for used_delay in self._batch_tick_stats:
                    if used_delay < 0:
                        logger.warning(
                            f"MessageFunnel: batching took longer than tick, delta time was {used_delay:.4f}"
                        )
                        break

                del self._batch_tick_stats[:]

                # cancel task if degraded for too long
                # UPDATE: removed as it might just be a slow connection or something
                # having warning logs about the degraded MessageFunnel should be enough for now.
                # simply stopping updates would not be a good user experience
                # however: Might want to publish messages about batch degradation to the client somehow.
                # if self._degraded_watchdog_count >= 30:
                #     logger.error(
                #         "MessageFunnel: batching was degraded for too long, batching was canceled!"
                #     )
                #     self.disable_batching_task()
                #     return

        except asyncio.CancelledError as e:
            logger.info("message funnel watchdog task has been canceled")
            raise e
        except Exception as e:
            logger.warning("message funnel watchdog had an exception:")
            logger.exception(e)
