import asyncio
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter

from asyncua.client.ua_client import UaClientState
from asyncua.common.events import Event
from asyncua.common.node import Node
from asyncua.common.subscription import (
    DataChangeEvent,
    OpcEvent,
    StatusChangeEvent,
    Subscription,
)
from asyncua.ua import NodeId, StatusCode
from asyncua.ua.attribute_ids import AttributeIds

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_session.session import OPCSession
from opensmi_ui.opc_session.task import StoppableTask, wait_or_stop

logger = get_module_logger("opc_subscriber")


DEFAULT_SUBSCRIPTION_PERIOD_MS = 200
SUBSCRIPTION_ADD_CHUNK_SIZE = 200
SUBSCRIPTION_REMOVE_CHUNK_SIZE = 200


@dataclass
class SubscribeDataRequest:
    node_id: NodeId
    attr: AttributeIds
    handler: Callable[[Node, DataChangeEvent], None]


@dataclass
class SubscribeEventRequest:
    node_id: NodeId
    handler: Callable[[Event], None]


@dataclass
class SubscriptionHandles:
    data_change_handles: list
    event_handles: list


class OPCSubscriber:
    opc_session: OPCSession

    subscription: Subscription | None

    handler_task: StoppableTask

    data_handlers: dict[NodeId, Callable[[Node, DataChangeEvent], None]]
    event_handlers: dict[NodeId, Callable[[Event], None]]

    def __init__(self, opc_session: OPCSession):
        self.opc_session = opc_session
        self.subscription = None
        self.handler_task = StoppableTask(worker=self.handler_worker)
        self.data_handlers = {}
        self.event_handlers = {}

    async def start(self):
        await self.handler_task.start()

    async def close(self):
        await self.handler_task.stop()

    async def add_subscription_batch(
        self,
        subscription_request_list: list[SubscribeDataRequest | SubscribeEventRequest],
    ) -> SubscriptionHandles:
        if self.subscription is None:
            raise RuntimeError("Cannot add subscriptions to a non-ready subscription")

        if not self.opc_session.is_connected():
            raise RuntimeError("Cannot add subscriptions to a non-connected session")

        handles = SubscriptionHandles(data_change_handles=[], event_handles=[])

        logger.info("Requesting %d Subscriptions", len(subscription_request_list))
        total = len(subscription_request_list)

        for start in range(0, total, SUBSCRIPTION_ADD_CHUNK_SIZE):
            chunk_start = perf_counter()
            chunk = subscription_request_list[
                start : start + SUBSCRIPTION_ADD_CHUNK_SIZE
            ]

            data_by_attr: dict[AttributeIds, list[SubscribeDataRequest]] = defaultdict(
                list
            )
            event_requests: list[SubscribeEventRequest] = []

            # proxy requests to either attr chunks or event
            for req in chunk:
                if isinstance(req, SubscribeDataRequest):
                    data_by_attr[req.attr].append(req)
                elif isinstance(req, SubscribeEventRequest):
                    event_requests.append(req)

            # create data change subs per attribute
            for attr, reqs in data_by_attr.items():
                # needing nodes here, although internally only node_id is used. Weird.
                nodes = [self.opc_session.opc_client.get_node(r.node_id) for r in reqs]

                # returns one handle or StatusCode per node
                results = await self.subscription.subscribe_data_change(
                    nodes, attr=attr
                )

                # check results and add handler it status code is ok
                for req, result in zip(reqs, results):
                    if isinstance(result, StatusCode):
                        logger.warning(
                            "Data subscription for %s (%s) failed: %s",
                            req.node_id,
                            attr.name,
                            result,
                        )
                    else:
                        # only keep track of subscriptions that actually worked
                        handles.data_change_handles.append(result)
                        self.data_handlers[req.node_id] = req.handler

            # events do not seem to be batchable at this time without going to monitored items
            for req in event_requests:
                try:
                    evt_handle = await self.subscription.subscribe_events(
                        self.opc_session.opc_client.get_node(req.node_id)
                    )
                    handles.event_handles.append(evt_handle)
                except Exception:
                    logger.exception("Event subscription for %s failed", req.node_id)
                else:
                    self.event_handlers[req.node_id] = req.handler

            logger.info(
                "Created subscriptions %d-%d of %d in %.6f seconds",
                start + 1,
                start + len(chunk),
                total,
                perf_counter() - chunk_start,
            )

        return handles

    async def clear_subscription_handles(self, handles: SubscriptionHandles):
        if self.subscription is None:
            raise RuntimeError("Cannot add subscriptions to a non-ready subscription")

        if not self.opc_session.is_connected():
            raise RuntimeError("Cannot add subscriptions to a non-connected session")

        all_handles = handles.data_change_handles + handles.event_handles

        for idx in range(0, len(all_handles), SUBSCRIPTION_REMOVE_CHUNK_SIZE):
            await self.subscription.unsubscribe(
                all_handles[idx : idx + SUBSCRIPTION_REMOVE_CHUNK_SIZE]
            )

    # react to server states
    def receive_server_state(self, new_state: UaClientState) -> None:
        match new_state:
            case UaClientState.CONNECTED:
                ...
                # probably racy, needs different solution
                # asyncio.create_task(self.start())
            case UaClientState.DISCONNECTED | UaClientState.DISCONNECTING:
                asyncio.create_task(self.close())

    # handler
    async def handler_worker(self, stop_event: asyncio.Event) -> None:
        if not self.opc_session.is_connected():
            raise RuntimeError(
                f"Cannot create subscriptions when OPCSession is not connected (State: {self.opc_session.opc_client.state})"
            )

        logger.info("Creating Subscription Worker")

        async with await self.opc_session.opc_client.create_subscription(
            period=DEFAULT_SUBSCRIPTION_PERIOD_MS, handler=None
        ) as subscription:
            self.subscription = subscription

            while not stop_event.is_set():
                event = await wait_or_stop(subscription.__anext__(), stop_event)

                if event is None:
                    break

                match event:
                    case DataChangeEvent(node=node):
                        if node.nodeid in self.data_handlers:
                            try:
                                self.data_handlers[node.nodeid](node, event)
                            except Exception:
                                logger.exception("failed to handle data change event")
                    case OpcEvent(event=event_data):
                        if event.event.emitting_node in self.event_handlers:
                            try:
                                self.event_handlers[event.event.emitting_node](
                                    event_data
                                )
                            except Exception:
                                logger.exception("failed to handle data change event")
                    case StatusChangeEvent(notification=notification):
                        logger.warning(
                            "Status of Subscription in Worker changed: %s",
                            notification.Status,
                        )

                        if notification.Status.is_bad():
                            break
                    case _:
                        logger.info("Unexpected Event: %s", event)

        self.subscription = None
        logger.info("Stopping Subscription Worker")
