import uuid
from collections import deque
from collections.abc import Iterable, Mapping
from uuid import uuid4

from asyncua.ua import SecurityPolicyType
from opensmi.client import (
    BaseRemoteComponent,
    RemoteMachine,
    RemoteServer,
    RemoteServerStatus,
    RemoteVariable,
)
from opensmi.client.browse import BrowseRule

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.common import JsonBaseModel
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
    state: RemoteServerStatus

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
    def __init__(self, settings: OPCClientSettings):
        self._settings = settings

        self.client: RemoteServer | None = None

        self.node_id_entity_id_cache = NodeIdEntityIdCache()

        self._callable_cache = EntityIdCallableCache()
        self._component_cache = EntityIdComponentCache()
        self._variable_cache = EntityIdVariableCache()

        self.session_data = OPCClientSessionData(
            application_uri=f"urn:smartfactory-kl:opensmi_ui:{uuid4()}",
            product_uri="urn:smartfactory-kl:opensmi_ui:session",
            settings=settings,
            username="",
            url="",
            browse_rules=None,
            security_policy=SecurityPolicyType.NoSecurity,
            state=RemoteServerStatus.DISCONNECTED,
        )

    def get_session_data(self):
        return self.session_data

    def clear_session_data(self):
        self.session_data.username = ""
        self.session_data.url = ""
        self.session_data.browse_rules = None
        self.session_data.security_policy = SecurityPolicyType.NoSecurity
        self.session_data.state = RemoteServerStatus.DISCONNECTED

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

        await self.client.connect()

        self.add_references_from_server(self.client.machines)

    def add_references_from_server(self, machines: Mapping[str, RemoteMachine]):
        for machine in machines.values():
            components_to_process = deque[BaseRemoteComponent]([machine])

            # TODO: Should really use the visitor pattern, as this chirade is also needed
            # to get the signals
            while components_to_process:
                next_component = components_to_process.popleft()
                self._component_cache.add(uuid.uuid4(), next_component)

                # handle callables
                for skill_container in [
                    next_component.skill_set,
                    next_component.feasibility_check_set,
                    next_component.precondition_check_set,
                ]:
                    for skill in skill_container.values():
                        self._callable_cache.add(uuid.uuid4(), skill)

                        # handle skill variable trees
                        for var_container in [
                            skill.monitoring,
                            skill.parameter_set,
                            skill.final_result_data,
                        ]:
                            for variable in var_container:
                                self._add_var_container_references(variable)

                for method in next_component.method_set.values():
                    self._callable_cache.add(uuid.uuid4(), method)
                    # handle skill variable trees
                    for var_container in [
                        method.monitoring,
                        method.parameter_set,
                        method.final_result_data,
                    ]:
                        for variable in var_container:
                            self._add_var_container_references(variable)

                # handle component variable trees
                for var_container in [
                    next_component.monitoring,
                    next_component.attributes,
                    next_component.identification,
                    next_component.parameter_set,
                ]:
                    for variable in var_container:
                        self._add_var_container_references(variable)

                for child in next_component.components.values():
                    components_to_process.append(child)

    def _add_var_container_references(self, variable: RemoteVariable):
        vars_to_process = deque[RemoteVariable]([variable])

        while vars_to_process:
            var_to_process = vars_to_process.popleft()
            self._variable_cache.add(uuid.uuid4(), var_to_process)

            for var_child in var_to_process.children.values():
                vars_to_process.append(var_child)

    async def close(self):
        await self.disconnect()

    async def disconnect(self):
        if self.client is None or self.client.status is RemoteServerStatus.DISCONNECTED:
            return

        await self.client.disconnect()

        self.clear_session_data()
