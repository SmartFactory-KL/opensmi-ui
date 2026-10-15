import asyncio
from uuid import uuid4

from asyncua import ua
from asyncua.client.client import Client
from asyncua.client.ua_client import UaClientState
from asyncua.ua import Int16
from asyncua.ua.uaerrors import BadNodeIdUnknown

from opensmi_ui.logger import get_module_logger
from opensmi_ui.messages.receiver import MessageReceiver
from opensmi_ui.model.common import JsonBaseModel, JsonOutModel

logger = get_module_logger("opc_session")


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
        msg_receiver: MessageReceiver,
        settings: OPCSessionSettings | None = None,
    ):
        """Create a new OPC Session while sending session updates to the msg_receiver. settings are optional and will be
        set to default values if not present. This only creates the session, it does not connect. To do that, call the connect() method."""
        if settings is None:
            settings = OPCSessionSettings()

        self._session_data = OPCSessionData(
            settings=settings,
            application_uri=f"urn:smartfactory-kl:opensmi_ui:{uuid4()}",
            product_uri="urn:smartfactory-kl:opensmi_ui:session",
        )

        self.msg_receiver = msg_receiver

        self.opc_client: Client = Client(
            url=""
        )  # this is only a dummy client to prevent None
        self._connection_monitor_task: asyncio.Task[None] | None = None

        self._namespaces: list[str] = []
        self._ns_idx_uri: dict[int, str] = {}
        self._ns_uri_idx: dict[str, ua.Int16] = {}

        self._type_defs: dict[str, type] = {}

    async def start(self) -> None:
        await self._start_connection_monitor()

    async def close(self) -> None:
        await self._stop_connection_monitor()
        await self.disconnect()

    async def _start_connection_monitor(self):
        # if the task is already running: stop and restart
        # this is needed because every reconnect is a new client
        # because the url could be different
        if (
            self._connection_monitor_task is not None
            and not self._connection_monitor_task.done()
        ):
            await self._stop_connection_monitor()

        logger.info("Starting Connection Monitor Task")
        self._connection_monitor_task = asyncio.create_task(self._connection_monitor())

    async def _stop_connection_monitor(self):
        if self._connection_monitor_task is None:
            return

        self._connection_monitor_task.cancel()

        try:
            await self._connection_monitor_task
        except asyncio.CancelledError:
            pass
        finally:
            self._connection_monitor_task = None

    async def connect(self, url: str, username: str, password: str) -> None:
        if (
            self.opc_client is not None
            and self.opc_client.state is not UaClientState.DISCONNECTED
        ):
            raise OPCSessionAlreadyConnectedError(
                f"Cannot connect: Client exists and not in state Disconnected (actual state is {self.opc_client.state})"
            )

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

        await self._start_connection_monitor()

        try:
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

        except:
            logger.exception("Failed to connect")
            raise

        self._session_data.username = username

        self._namespaces = await self.opc_client.get_namespace_array()
        self._ns_idx_uri.clear()
        self._ns_uri_idx.clear()

        for idx, _ns in enumerate(self._namespaces):
            self._ns_idx_uri[idx] = _ns
            self._ns_uri_idx[_ns] = ua.Int16(idx)

        self._type_defs = await self.opc_client.load_data_type_definitions()

        self._session_data.namespaces = self._namespaces

    async def disconnect(self) -> None:
        if self.opc_client is None:
            return

        try:
            await self.opc_client.disconnect()
            self._clear_session_data()
        except ConnectionError:
            logger.warning("Disconnect was called but got ConnectionError")
            return
        except Exception:
            raise

        self._session_data.username = ""

    async def _connection_monitor(self) -> None:
        if self.opc_client is None:
            logger.warning("Connection monitor cannot work while opc_client is None")
            return

        async with self.opc_client.subscribe_state() as conn_state:
            while True:
                state = await conn_state.next_change()
                logger.info(f"Session now in {state}")
                self._session_data.state = state

                # this is created as a task to not slow down the monitor
                # because of slow connections
                asyncio.create_task(self.msg_receiver.receive_server_state(state))

    def namespace_idx(self, uri: str) -> Int16:
        try:
            return self._ns_uri_idx[uri]
        except KeyError:
            raise ValueError(f"Unknown namespace URI: {uri!r}") from None

    def namespace_uri(self, idx: int) -> str:
        try:
            return self._namespaces[idx]
        except ValueError:
            raise ValueError(f"Unknown namespace index: {idx}") from None

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
