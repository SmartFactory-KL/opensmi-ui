import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Mapping

from pyuaadapter.client.remote_server import (
    RemoteServer,
    RemoteServerStatus,
    RemoteServerSubscriber,
)
from pyuaadapter.common.subscription_manager import SubscriptionManager
from typing_extensions import override

import app_config
from messages.message_funnel import MessageFunnel
from model.common_types import GenericActionRequest, GenericActionTargetEntityType
from model.server_types import (
    ServerConnectionState,
    ServerConnectionUpdate,
    ServerConnectRequest,
    ServerDefaultConnectionDataResponse,
    ServerStateResponse,
    ServerTimeUpdate,
    ServerUpdateMessage,
)
from opc_client.machine_module import MachineModule
from opc_client.reference_store import NodeEntityStore, ReferenceStore
from opc_locking.locking_module import LockingConfiguration
from pin_guard.pin_guard import PinGuard
from util.serialize import serialize_data_value

logger = logging.getLogger("uvicorn")

msg_funnel = MessageFunnel()
reference_store = ReferenceStore()
node_entity_store = NodeEntityStore()


class ServerModule(RemoteServerSubscriber):
    _self = None

    server: RemoteServer
    connection_state: ServerConnectionState = ServerConnectionState.Open
    entity_id: uuid.UUID

    # maps entity ids to machines
    server_machine_map: dict[uuid.UUID, MachineModule]

    # reference used when a force disconnect is requested
    # should point to the (very low level) tcp transport
    # INFO: Was mostly relevant whenever people would use breakpoints while developing
    # INFO: for the pyuaadapter server.
    force_disconnect_transport_reference: Any

    # pin guard (only relevant if enabled)
    pin_guard: PinGuard

    # these are only used to provide as information
    server_url: str = ""
    username: str = ""

    # these are only relayed from environment
    default_server_url: str = ""
    default_server_username: str = ""
    default_server_password: str = ""

    # used primarily for the RemoteVariable
    subscription_manager: SubscriptionManager

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self):
        self.connection_state = ServerConnectionState.Open
        self.entity_id = uuid.uuid4()

    def read_defaults(self):
        """Read default values for server connection data and pin guard options"""
        self.default_server_url = app_config.get_text("OPC_UA_DEFAULT_SERVER_URL")
        self.default_server_username = app_config.get_text(
            "OPC_UA_DEFAULT_SERVER_USERNAME"
        )
        self.default_server_password = app_config.get_text(
            "OPC_UA_DEFAULT_SERVER_PASSWORD"
        )

        self.pin_guard = PinGuard(
            is_enabled=app_config.is_set("PIN_GUARD_ENABLED"),
            pin=app_config.get_text("PIN_GUARD_PIN"),
            autolock_delay=app_config.get_int("PIN_GUARD_AUTOLOCK_DELAY_SECONDS"),
        )

    async def request_connect(
        self, data: ServerConnectRequest, is_auto_connect_request: bool = False
    ):
        """Create a request to connect to an OPC UA server"""
        logger.info("Requesting connection...")

        # PinGuard should not prevent AutoConnects, only UI based connects
        if not is_auto_connect_request:
            self.check_pin_guard()

        if self.connection_state == ServerConnectionState.Connected:
            msg = "Server is already connected. Disconnect first."
            logger.warning(msg)
            raise Exception(msg)

        if self.connection_state != ServerConnectionState.Open:
            msg = (
                "ServerConnectionState is "
                + self.connection_state
                + " instead of open. Aborted."
            )
            logger.warning(msg)
            raise Exception(msg)

        self.connection_state = ServerConnectionState.Pending
        self.broadcast_connection_state()

        msg_funnel.enable_batching_task()

        try:
            if app_config.is_set("SERVER_ONLY_ALLOW_DEFAULT_CONNECTION_DATA"):
                logger.info(
                    "+++ ONLY_ALLOW_PRESET_CONNECTION_DATA is set, connect() will use default connection data! +++"
                )
                data.server_url = self.default_server_url
                data.username = self.default_server_username
                data.password = self.default_server_password

            # create actual connection.
            self.server = RemoteServer(
                url=data.server_url, username=data.username, password=data.password
            )

            self.server.add_subscriber(self)
            self.username = data.username

            timeout_seconds = app_config.get_int("OPC_UA_CONNECT_REQUEST_TIMEOUT_SECONDS")
            if timeout_seconds <= 0:
                raise ValueError("OPC_UA_CONNECT_REQUEST_TIMEOUT_SECONDS has to be at least 1 or greater")

            _ = await self.server.connect(timeout=timeout_seconds, max_retries=0)

            self.server_url = data.server_url

            return ServerStateResponse(
                connection_state=ServerConnectionState.Open,  # <- not used!
                server_url=data.server_url,
                username=data.username,
                pin_guard_state=self.pin_guard.get_state(),
            )
        except Exception as e:
            logger.warning("Unable to connect.")
            logger.warning(e)
            self.connection_state = ServerConnectionState.Open
            self.broadcast_connection_state()
            msg_funnel.disable_batching_task()
            raise e

    async def request_disconnect(self, force: bool = False) -> None:
        """Request a (forced) disconnect or cancel a pending connection"""
        logger.info("Requesting disconnect...")

        self.check_pin_guard()

        if force:
            logger.warning("#######################################")
            logger.warning("# A FORCE DISCONNECT WAS CALLED       #")
            logger.warning("#######################################")
            if self.server is not None:
                await self.server.disconnect()

                logger.warning("Try to close the actual transport")
                logger.warning(self.force_disconnect_transport_reference)
                if self.force_disconnect_transport_reference is not None and hasattr(
                    self.force_disconnect_transport_reference, "close"
                ):
                    self.force_disconnect_transport_reference.close()

                self.on_connection_lost()
        else:
            if (
                self.server is not None
                and self.connection_state != ServerConnectionState.Open
            ):
                await self.server.disconnect()
                self.on_connection_lost()
            else:
                logger.info("Server already disconnected.")

    def is_connected(self):
        """Get the current connection state"""
        return self.connection_state == ServerConnectionState.Connected

    def get_server_state(self):
        """Get the current overall state of the server"""
        return ServerStateResponse(
            connection_state=self.connection_state,
            server_url=self.server_url,
            username=self.username,
            pin_guard_state=self.pin_guard.get_state(),
        )

    def get_default_connection_data(self):
        """Get the default values set by environment"""
        return ServerDefaultConnectionDataResponse(
            default_server_url=self.default_server_url,
            default_server_username=self.default_server_username,
            default_server_password=self.default_server_password,
            is_in_only_preset_mode=app_config.is_set(
                "SERVER_ONLY_ALLOW_DEFAULT_CONNECTION_DATA"
            ),
        )

    def get_machine(self, machine_entity_id: uuid.UUID):
        return self.server_machine_map.get(machine_entity_id)

    async def get_machine_list(self):
        """Get the list of machines on this server"""
        if not self.is_connected() or self.server is None:
            return []

        result = []

        for _, _machine in self.server_machine_map.items():
            machine_dto = await _machine.to_dto()
            result.append(machine_dto)

        return result

    # Pin Guard for external use
    def get_pin_guard(self):
        return self.pin_guard

    def check_pin_guard(self):
        if not self.pin_guard.check():
            raise Exception("PinGuard is locked. Action was not allowed.")
        else:
            # tick the Pin Guard to reset the delay for auto_lock
            self.pin_guard.tick_auto_lock()

    # Actions Proxy through Pin Guard
    # ---------------------------------------------
    async def proxy_action(self, action: GenericActionRequest):
        """
        Used in combination with request_xxx_action to proxy
        an action to the desired entity while using PinGuard (if enabled)
        """
        logger.info("Action requested")
        logger.info(action)

        self.check_pin_guard()

        match action.entity_type:
            case GenericActionTargetEntityType.Skill:
                await self.request_skill_action(action)
            case GenericActionTargetEntityType.Method:
                await self.request_method_action(action)
            case GenericActionTargetEntityType.Component:
                await self.request_component_action(action)
            case GenericActionTargetEntityType.Machine:
                await self.request_machine_action(action)
            case _:
                raise Exception("Invalid target_entity_type for Action. Ignored.")

    async def request_skill_action(self, skill_action: GenericActionRequest):
        target_skill = reference_store.get_skill(skill_action.entity_id)

        if target_skill is None:
            raise Exception("No target skill found for SkillAction")

        await target_skill.apply_skill_action(skill_action)

    async def request_method_action(self, method_action: GenericActionRequest):
        target_method = reference_store.get_method(method_action.entity_id)

        if target_method is None:
            raise Exception("No target method found for MethodAction")

        await target_method.apply_method_action(method_action)

    async def request_component_action(self, component_action: GenericActionRequest):
        target_component = reference_store.get_component(component_action.entity_id)

        if target_component is None:
            raise Exception("No target component found for ComponentAction")

        await target_component.apply_component_action(component_action)

    async def request_machine_action(self, machine_action: GenericActionRequest):
        target_machine = reference_store.get_machine(machine_action.entity_id)
        print(target_machine)

        if target_machine is None:
            raise Exception("No target machine found for MachineAction")

        await target_machine.apply_machine_action(machine_action)

    # Proxy for History Request
    async def request_node_history(
        self, node_entity_id: uuid.UUID, limit: int = 100, timedelta_hours: int = 1
    ):
        target_variable = reference_store.get_remote_variable(
            remote_variable_entity_id=node_entity_id
        )

        if target_variable is None:
            raise Exception("No Variable found for entityId")

        history_start = datetime.now(timezone.utc) - timedelta(hours=timedelta_hours)
        history_end = datetime.now(timezone.utc)

        history = await target_variable.remote_remote_variable.ua_node.read_raw_history(
            starttime=history_start,
            endtime=history_end,
        )
        # Why reverse twice? (here and on return)
        # The history has nothing regarding a forced order. To get the list of
        # the most recent ones, I need to sort them in descending order according to timestamp
        # (which is the first reverse)
        # Since the frontend expects the oldest values to be in the lower indices,
        # I need to reverse again. But without the first reverse, it could get the 100 oldest values
        history.sort(key=lambda el: el.ServerTimestamp, reverse=True)

        serialized_history = list(map(serialize_data_value, history[:limit]))
        serialized_history.reverse()
        return serialized_history

    # Subscriber
    # ---------------------------------------------

    @override
    def on_status_change(self, status: RemoteServerStatus) -> None:
        match status:
            case RemoteServerStatus.CONNECTED:
                self.connection_state = ServerConnectionState.Connected
            case RemoteServerStatus.DISCONNECTED:
                self.connection_state = ServerConnectionState.Open
            case RemoteServerStatus.CONNECTING:
                self.connection_state = ServerConnectionState.Pending
            case RemoteServerStatus.BROWSING:
                self.connection_state = ServerConnectionState.Browsing
        self.broadcast_connection_state()

    @override
    def on_connection_established(self):
        reference_store.clear()
        node_entity_store.clear()

        self.server_machine_map.clear()

        lock_config = LockingConfiguration(
            is_enabled=app_config.is_set("LOCKING_ENABLED"),
            is_simulated=app_config.is_set("LOCKING_SIMULATION_ENABLED"),
            autofree_delay_seconds=app_config.get_int("LOCKING_AUTOFREE_DELAY_SECONDS"),
            locking_simulation_username=self.username,
        )

        self.subscription_manager = self.server.subscription_manager

        for _machine in self.server.machines.values():
            new_machine_module = MachineModule(
                input_remote_machine=_machine,
                parent_server=self.server,
                reference_store=reference_store,
                node_entity_store=node_entity_store,
                lock_config=lock_config,
                subscription_manager=self.server.subscription_manager,
            )
            self.server_machine_map[new_machine_module.entity_id] = new_machine_module

        self.force_disconnect_transport_reference = (
            self.server._ua_client.uaclient.protocol.transport
        )

        msg_funnel.enable_batching_task()

    @override
    def on_connection_lost(self):
        logger.info("on_connection_lost")

        for _, machine in self.server_machine_map.items():
            machine.on_server_disconnect()

        reference_store.clear()
        node_entity_store.clear()

        msg_funnel.disable_batching_task()

    @override
    def on_server_time_update(self, current_server_time: datetime):
        msg = ServerUpdateMessage[ServerTimeUpdate](
            entity_id=self.entity_id,
            update_content=ServerTimeUpdate(
                new_datetime=current_server_time.isoformat()
            ),
        )
        msg_funnel.send_direct_message(msg)

    def broadcast_connection_state(self):
        msg = ServerUpdateMessage[ServerConnectionUpdate](
            entity_id=self.entity_id,
            update_content=ServerConnectionUpdate(
                connection_state=self.connection_state
            ),
        )

        msg_funnel.send_direct_message(msg)
        msg_funnel.send_refresh_signal()
