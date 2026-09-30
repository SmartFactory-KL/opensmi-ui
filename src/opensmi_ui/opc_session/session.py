import asyncio
from uuid import uuid4

from asyncua import ua
from asyncua.client.client import Client
from asyncua.client.ua_client import UaClientState
from asyncua.ua import Int16

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.common import JsonBaseModel, JsonOutModel

logger = get_module_logger("opc_session")


class OPCSessionNotReadyError(Exception):
    """can be raised when the session is not ready yet but was intended to be used"""


class OPCSessionSettings(JsonBaseModel):
    timeout: float = 30.0
    auto_reconnect: bool = True

    reconnect_max_delay: float = 60.0
    watchdog_intervall: float = 5.0

    reconnect_request_timeout: float = 60.0


class OPCSessionData(JsonOutModel):
    username: str = ""
    state: UaClientState = UaClientState.DISCONNECTED

    application_uri: str = ""

    namespaces: list[str] | None = None

    session_settings: OPCSessionSettings | None = None


class OPCSession:
    def __init__(
        self,
        url: str,
        settings: OPCSessionSettings | None = None,
    ):
        if settings is None:
            settings = OPCSessionSettings()

        self._opc_session_settings = settings

        self.opc_client = Client(
            url=url,
            timeout=settings.timeout,
            auto_reconnect=settings.auto_reconnect,
            reconnect_max_delay=settings.reconnect_max_delay,
            reconnect_request_timeout=settings.reconnect_request_timeout,
            watchdog_intervall=settings.watchdog_intervall,
        )

        self.opc_client.application_uri = f"urn:smartfactory-kl:opensmi_ui:{uuid4()}"
        self.opc_client.product_uri = "urn:smartfactory-kl:opensmi_ui:session"

        self._connection_monitor_task: asyncio.Task[None] | None = None

        self._namespaces: list[str] = []
        self._ns_idx_uri: dict[int, str] = {}
        self._ns_uri_idx: dict[str, ua.Int16] = {}

        self._type_defs: dict[str, type] = {}

        self._info = OPCSessionData(
            application_uri=self.opc_client.application_uri,
            session_settings=self._opc_session_settings,
        )

    async def _connection_monitor(self) -> None:
        async with self.opc_client.subscribe_state() as conn_state:
            while True:
                state = await conn_state.next_change()
                self._info.state = state
                logger.info(f"Session now in {state}")

    async def start(self) -> None:
        if (
            self._connection_monitor_task is not None
            and not self._connection_monitor_task.done()
        ):
            return

        logger.info("Starting Connection Monitor Task")
        self._connection_monitor_task = asyncio.create_task(self._connection_monitor())

    async def close(self) -> None:
        if self._connection_monitor_task is None:
            return

        self._connection_monitor_task.cancel()

        try:
            await self._connection_monitor_task
        except asyncio.CancelledError:
            pass
        finally:
            self._connection_monitor_task = None

    async def connect(self, username: str, password: str) -> None:
        if self.opc_client.state != UaClientState.DISCONNECTED:
            raise ValueError(
                f"Connection is currently in {self.opc_client.state}, please disconnect or wait for {UaClientState.DISCONNECTED} before connecting again"
            )

        self.opc_client.set_user(username)
        self._info.username = username

        self.opc_client.set_password(password)

        await self.opc_client.connect(
            auto_reconnect=self._opc_session_settings.auto_reconnect,
            reconnect_max_delay=self._opc_session_settings.reconnect_max_delay,
            reconnect_request_timeout=self._opc_session_settings.reconnect_request_timeout,
        )

        self._namespaces = await self.opc_client.get_namespace_array()
        self._ns_idx_uri.clear()
        self._ns_uri_idx.clear()

        for idx, _ns in enumerate(self._namespaces):
            self._ns_idx_uri[idx] = _ns
            self._ns_uri_idx[_ns] = ua.Int16(idx)

        self._type_defs = await self.opc_client.load_data_type_definitions()

        self._info.namespaces = self._namespaces

    async def disconnect(self) -> None:
        await self.opc_client.disconnect()

        self._info.username = ""

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

    def get_info(self) -> OPCSessionData:
        return self._info

    def is_ready(self) -> bool:
        return self.opc_client.state is UaClientState.CONNECTED
