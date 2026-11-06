from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from asyncua import ua
from asyncua.client.client import Client
from asyncua.client.ua_client import UaClientState
from asyncua.common.subscription import (
    DataChangeEvent,
    OpcEvent,
    StatusChangeEvent,
)
from asyncua.ua.uaerrors import BadNodeIdUnknown

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.json import JsonBaseModel, JsonOutModel
from opensmi_ui.opc_session.namespace import OPCNamespace
from opensmi_ui.opc_session.task import StoppableTask

logger = get_module_logger("opc_session")

__all__ = [
    "OPCSession",
    "OPCSessionAlreadyConnectedError",
    "OPCSessionConnectRequest",
    "OPCSessionData",
    "OPCSessionNotReadyError",
    "OPCSessionSettings",
]

ConnectionStateChangedHandler = Callable[[UaClientState], None]
ConnectionSessionChangedHandler = Callable[["OPCSessionData"], None]
TimeChangedHandler = Callable[[datetime], None]
SessionIsReadyChangedHandler = Callable[[bool], None]


class OPCSessionNotReadyError(Exception):
    """can be raised when the session is not ready yet but was intended to be used"""


class OPCSessionAlreadyConnectedError(Exception):
    """can be raised to indicate that session is already connected"""


class OPCSessionConnectRequest(JsonBaseModel):
    url: str = ""
    username: str = ""
    password: str = ""


class OPCSessionSettings(JsonBaseModel):
    timeout: float = 30.0
    auto_reconnect: bool = True

    reconnect_max_delay: float = 60.0
    watchdog_intervall: float = 5.0

    reconnect_request_timeout: float = 60.0

    time_subscription_sampling_interval_ms: float = 500.0


class OPCSessionData(JsonOutModel):
    url: str = ""
    username: str = ""

    state: UaClientState = UaClientState.DISCONNECTED

    application_uri: str = ""
    product_uri: str = ""
    namespaces: list[str] | None = None

    settings: OPCSessionSettings


class OPCSession:
    def __init__(
        self,
        settings: OPCSessionSettings | None = None,
    ) -> None:
        """Create a new OPC Session. Settings are optional and fall back to
        default values. This only creates the session, it does not connect.
        To do that, call the connect() method."""
        if settings is None:
            settings = OPCSessionSettings()

        self._session_data: OPCSessionData = OPCSessionData(
            settings=settings,
            application_uri=f"urn:smartfactory-kl:opensmi_ui:{uuid4()}",
            product_uri="urn:smartfactory-kl:opensmi_ui:session",
        )

        # only a dummy client to prevent None
        self.opc_client: Client = Client(url="")

        self._is_ready: bool = False
        """This captures the dangling state in between being connected but not yet ready.
        Namespaces for example should only be read after _is_ready is True"""

        self._connection_monitor_task: StoppableTask = StoppableTask(
            worker=self._connection_monitor_worker
        )
        self._time_change_task: StoppableTask = StoppableTask(
            worker=self._time_change_worker
        )

        self._namespace: OPCNamespace = OPCNamespace()
        self._type_defs: dict[str, type] = {}

        self._connection_state_changed_handler: set[ConnectionStateChangedHandler] = (
            set()
        )
        self._connection_session_changed_handler: set[
            ConnectionSessionChangedHandler
        ] = set()
        self._time_changed_handler: set[TimeChangedHandler] = set()
        self._is_ready_changed_handler: set[SessionIsReadyChangedHandler] = set()

    @property
    def namespace(self):
        if not self._namespace.is_ready():
            raise OPCSessionNotReadyError("Namespace is not ready to use")

        return self._namespace

    async def start(self) -> None:
        await self._connection_monitor_task.start()

    async def close(self) -> None:
        await self._connection_monitor_task.stop()
        await self._time_change_task.stop()

        await self.disconnect()

    async def connect(self, url: str, username: str, password: str) -> None:
        if (
            self.opc_client is not None
            and self.opc_client.state is not UaClientState.DISCONNECTED
        ):
            raise OPCSessionAlreadyConnectedError(
                f"Cannot connect: Client exists and not in state Disconnected (actual state is {self.opc_client.state})"
            )

        self._is_ready = False
        self._namespace.reset()

        settings = self._session_data.settings

        self.opc_client = Client(
            url=url,
            timeout=settings.timeout,
            auto_reconnect=settings.auto_reconnect,
            reconnect_max_delay=settings.reconnect_max_delay,
            reconnect_request_timeout=settings.reconnect_request_timeout,
            watchdog_intervall=settings.watchdog_intervall,
        )

        self.opc_client.set_user(username)
        self.opc_client.set_password(password)

        await self._connection_monitor_task.start()

        try:
            self._session_data.username = username
            self._session_data.url = url

            await self.opc_client.connect(
                auto_reconnect=settings.auto_reconnect,
                reconnect_max_delay=settings.reconnect_max_delay,
                reconnect_request_timeout=settings.reconnect_request_timeout,
            )

            # read operation limits
            try:
                operation_limits_node = self.opc_client.get_node(
                    ua.object_ids.ObjectIds.ServerCapabilitiesType_OperationLimits_MaxNodesPerBrowse
                )
                limit = await operation_limits_node.get_value()

                logger.info(
                    f"This server present an operation limit for MaxNodesPerBrowse: {limit}"
                )
            except BadNodeIdUnknown as e:
                logger.warning(f"No Operation Limits found: {e}")

            # read available reference types
            try:
                reference_types_folder_node = self.opc_client.get_node(
                    ua.object_ids.ObjectIds.NonHierarchicalReferences
                )

                reference_types = await reference_types_folder_node.get_children()
                logger.info("Available Reference Types:")

                for reference_type in reference_types:
                    logger.info(reference_type)

            except Exception as e:  # noqa: BLE001 # only used for informational purposes anyway
                logger.warning(f"Failed to read reference types: {e}")

            # create the time subscription
            await self._time_change_task.start()

            namespaces = await self.opc_client.get_namespace_array()
            self._namespace.update_namespaces(namespaces=namespaces)
            self._session_data.namespaces = namespaces

            self._type_defs = await self.opc_client.load_data_type_definitions()

            self._is_ready = True
        except:
            logger.exception("Failed to connect")
            await self._time_change_task.stop()
            raise

    async def disconnect(self) -> None:
        if self.opc_client is None:
            return

        try:
            self._is_ready = False
            await self._time_change_task.stop()
            await self.opc_client.disconnect()
            self._namespace.reset()
            self._clear_session_data()
        except ConnectionError:
            logger.warning("Disconnect was called but got ConnectionError")
            return
        except Exception:
            raise

        self._session_data.username = ""

    async def _connection_monitor_worker(self) -> None:
        if self.opc_client is None:
            logger.warning("Connection monitor cannot work while opc_client is None")
            return

        logger.info("Start Connection Monitor")
        async with self.opc_client.subscribe_state() as conn_state:
            while True:
                state = await conn_state.next_change()

                logger.info(f"Session now in {state}")
                self._session_data.state = state

                for handler in self._connection_state_changed_handler:
                    try:
                        handler(state)
                    except Exception as e:  # noqa: BLE001
                        # warning disabled because handlers are user defined and could raise anything
                        logger.warning(f"failed to handle connection state change: {e}")

                # broadcast new session data when connected
                if state in [UaClientState.CONNECTED, UaClientState.DISCONNECTED]:
                    for handler in self._connection_session_changed_handler:
                        try:
                            handler(self._session_data)
                        except Exception as e:  # noqa: BLE001
                            # warning disabled because handlers are user defined and could raise anything
                            logger.warning(
                                f"failed to handle connection session change: {e}"
                            )

    async def _time_change_worker(self) -> None:
        if self.opc_client is None:
            logger.warning("Time Monitor cannot work while opc_client is None")
            return

        logger.info("Start Time Monitor")

        current_time_node = self.opc_client.get_node(
            ua.object_ids.ObjectIds.Server_ServerStatus_CurrentTime
        )
        interval = self._session_data.settings.time_subscription_sampling_interval_ms

        async with await self.opc_client.create_subscription(
            period=interval,
            handler=None,
        ) as subscription:
            await subscription.subscribe_data_change(
                nodes=current_time_node,
                sampling_interval=ua.Duration(interval),
            )

            async for item in subscription:
                match item:
                    case DataChangeEvent(node=node, value=value):
                        if node == current_time_node:
                            for handler in self._time_changed_handler:
                                try:
                                    handler(value)
                                except Exception as e:  # noqa: BLE001
                                    # warning disabled because handlers are user defined and could raise anything
                                    logger.warning(f"failed to handle time change: {e}")

                    case OpcEvent(event=event_data):
                        logger.debug("Received OPC UA event: %s", event_data)
                    case StatusChangeEvent(notification=notification):
                        logger.info(
                            "Time subscription status changed: %s", notification.Status
                        )

                        if notification.Status.is_bad():
                            break

    def on_connection_state_changed(self, handler: ConnectionStateChangedHandler):
        self._connection_state_changed_handler.add(handler)

    def off_connection_state_changed(self, handler: ConnectionStateChangedHandler):
        self._connection_state_changed_handler.discard(handler)

    def on_connection_session_changed(self, handler: ConnectionSessionChangedHandler):
        self._connection_session_changed_handler.add(handler)

    def off_connection_session_changed(self, handler: ConnectionSessionChangedHandler):
        self._connection_session_changed_handler.discard(handler)

    def on_time_changed(self, handler: TimeChangedHandler):
        self._time_changed_handler.add(handler)

    def off_time_changed(self, handler: TimeChangedHandler):
        self._time_changed_handler.discard(handler)

    def on_is_ready_changed(self, handler: SessionIsReadyChangedHandler):
        self._is_ready_changed_handler.add(handler)

    def off_is_ready_changed(self, handler: SessionIsReadyChangedHandler):
        self._is_ready_changed_handler.discard(handler)

    def get_session_data(self) -> OPCSessionData:
        return self._session_data

    def _clear_session_data(self) -> None:
        self._session_data.username = ""
        self._session_data.namespaces = []

    def is_connected(self) -> bool:
        return (
            self.opc_client is not None
            and self.opc_client.state is UaClientState.CONNECTED
        )
