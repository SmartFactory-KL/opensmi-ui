from collections.abc import Awaitable, Iterable
from uuid import uuid4

from asyncua.ua import SecurityPolicyType
from opensmi.client import (
    RemoteServer,
    RemoteServerStatus,
)
from opensmi.client.browse import BrowseRule
from opensmi.core import Signal

from opensmi_ui.logger import get_module_logger
from opensmi_ui.messages.receiver import MessageReceiver
from opensmi_ui.model.common import JsonBaseModel
from opensmi_ui.opc_client.identifiable import ComponentEntityDTO
from opensmi_ui.opc_client.model import MachineryModel
from opensmi_ui.opc_client.reference import (
    EntityIdCallableCache,
    EntityIdComponentCache,
    EntityIdVariableCache,
    NodeIdEntityIdCache,
)

logger = get_module_logger("opc_client")


class OPCClientSettings(JsonBaseModel):
    auto_reconnect: bool = True
    reconnect_max_delay: float = 60.0
    reconnect_request_timeout: float = 60.0
    timeout: float = 30.0
    watchdog_interval: float = 5.0


class OPCClientSessionData(JsonBaseModel):
    state: str

    application_uri: str
    product_uri: str

    browse_rules: Iterable[BrowseRule] | None = None
    security_policy: SecurityPolicyType = SecurityPolicyType.NoSecurity

    url: str
    username: str

    settings: OPCClientSettings


class OPCClientConnectRequest(JsonBaseModel):
    url: str

    browse_rules: Iterable[BrowseRule] | None = None
    security_policy: SecurityPolicyType = SecurityPolicyType.NoSecurity

    username: str
    password: str


class OPCClientSessionNotReadyError(RuntimeError):
    """Raised whenever a connection request was made but the session was not ready for it"""

    def __init__(self, msg: str = "OPC Client is not ready"):
        super().__init__(msg)


class OPCClient:
    def __init__(self, settings: OPCClientSettings, msg_receiver: MessageReceiver):
        self._settings = settings

        self.client: RemoteServer | None = None

        self.model: MachineryModel = MachineryModel()

        self.node_id_entity_id_cache = NodeIdEntityIdCache()

        self._callable_cache = EntityIdCallableCache()
        self._component_cache = EntityIdComponentCache()
        self._variable_cache = EntityIdVariableCache()

        self._signals: dict[Signal, Awaitable] = {}
        self.receiver = msg_receiver
        self.session_data = OPCClientSessionData(
            application_uri=f"urn:smartfactory-kl:opensmi_ui:{uuid4()}",
            product_uri="urn:smartfactory-kl:opensmi_ui:session",
            settings=settings,
            username="",
            url="",
            browse_rules=None,
            security_policy=SecurityPolicyType.NoSecurity,
            state=RemoteServerStatus.DISCONNECTED.name,
        )

    def get_session_data(self):
        return self.session_data

    def clear_session_data(self):
        self.session_data.username = ""
        self.session_data.url = ""
        self.session_data.browse_rules = None
        self.session_data.security_policy = SecurityPolicyType.NoSecurity
        self.session_data.state = RemoteServerStatus.DISCONNECTED.name

    def get_machines(self) -> list[ComponentEntityDTO]:
        if self.client is None:
            return []

        return self.model.get_component_dtos()

    async def connect(self, request: OPCClientConnectRequest):
        if (
            self.client is not None
            and self.client.status is not RemoteServerStatus.DISCONNECTED
        ):
            raise OPCClientSessionNotReadyError(
                f"Can not connect because Client is not in state {RemoteServerStatus.DISCONNECTED} but in {self.client.status}"
            )

        self.client = RemoteServer(
            url=request.url,
            username=request.username,
            password=request.password,
        )

        self.clear_session_data()

        self.session_data.url = request.url
        self.session_data.username = request.username
        self.session_data.browse_rules = request.browse_rules
        self.session_data.security_policy = request.security_policy

        self.client.status_changed.connect(callback=self.receiver.receive_server_state)
        self.client.status_changed.connect(callback=self.update_state)

        self.client.time_updated.connect(callback=self.receiver.receive_server_time)

        await self.client.connect()

        self.model.create_from_client(self.client)
        self.model.connect_signals(self.receiver)

    async def update_state(self, new_state: RemoteServerStatus):
        self.session_data.state = new_state.name

    async def close(self):
        await self.disconnect()

    async def disconnect(self):
        if self.client is None or self.client.status is RemoteServerStatus.DISCONNECTED:
            return

        await self.client.disconnect()

        self.clear_session_data()
