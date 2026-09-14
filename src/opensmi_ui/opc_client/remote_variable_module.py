import asyncio
import logging
import uuid

from asyncua import Node
from asyncua.common.subscription import DataChangeNotif
from opc_client.reference_store import NodeEntityStore, ReferenceStore
from pyuaadapter.client.remote_variable import RemoteVariable
from pyuaadapter.common.subscription_manager import SubscriptionManager

from opensmi_ui.messages.message_funnel import MessageFunnel
from opensmi_ui.model.machine_types import (
    VariableDataValueUpdate,
    VariableUpdateMessage,
)
from opensmi_ui.model.node_types import RemoteVariableDto
from opensmi_ui.util.determine_type import determine_type_and_annotations
from opensmi_ui.util.serialize import serialize_data_value

logger = logging.getLogger("uvicorn")

msg_funnel = MessageFunnel()


class RemoteVariableModule:
    remote_remote_variable: RemoteVariable

    entity_id: uuid.UUID
    parent_entity_id: uuid.UUID | None

    children: list["RemoteVariableModule"]

    reference_store: ReferenceStore
    node_entity_store: NodeEntityStore

    subscription_manager: SubscriptionManager

    last_update_timestamp: float

    def __init__(
        self,
        input_remote_variable: RemoteVariable,
        reference_store: ReferenceStore,
        node_entity_store: NodeEntityStore,
        parent_entity_id: uuid.UUID | None,
        subscription_manager: SubscriptionManager,
    ):
        self.remote_remote_variable = input_remote_variable

        self.entity_id = uuid.uuid4()
        self.parent_entity_id = parent_entity_id

        self.children = []

        self.reference_store = reference_store
        self.node_entity_store = node_entity_store

        self.subscription_manager = subscription_manager

        for _remote_variable in self.remote_remote_variable.children.values():
            self.children.append(
                RemoteVariableModule(
                    input_remote_variable=_remote_variable,
                    reference_store=reference_store,
                    node_entity_store=node_entity_store,
                    parent_entity_id=self.entity_id,
                    subscription_manager=self.subscription_manager,
                ),
            )

        self.reference_store.add_remote_variable(self)
        self.node_entity_store.add_node_entity_reference(
            self.remote_remote_variable.ua_node.nodeid.to_string(), self.entity_id
        )

        self.last_update_timestamp = 0.0

        asyncio.create_task(self.init_subscription())

    async def init_subscription(self):
        node = self.remote_remote_variable.ua_node
        try:
            await self.subscription_manager.subscribe_data_change(
                handler=self,
                nodes=[node],
            )
        except Exception as e:
            logger.warning("Exception during subscription init")
            logger.warning(e)

    async def to_dto(self) -> RemoteVariableDto:
        basic_dto = self.remote_remote_variable.dto()

        type_data = determine_type_and_annotations(
            self.remote_remote_variable, basic_dto["ua_data_type"]
        )

        node = self.remote_remote_variable.ua_node
        data_value = None
        try:
            data_value = await node.read_data_value()
        except Exception as e:
            logger.error(e)

        serialized_value = serialize_data_value(data_value)

        data = {
            "name": basic_dto["name"],
            "entity_id": self.entity_id,
            "parent_entity_id": self.parent_entity_id,
            "node_id": basic_dto["node_id"],
            "data_content": serialized_value,
            "remote_variable_type": type_data.value_type,
            "remote_variable_annotation": type_data.value_annotation,
            "is_writable": basic_dto["is_writable"],
            "unit": basic_dto["unit"],
            "children": [await r.to_dto() for r in self.children],
        }

        return data

    def datachange_notification(self, node: Node, _: Any, data: DataChangeNotif):
        encoded_value = serialize_data_value(data.monitored_item.Value)

        target_node_id = node.nodeid.to_string()
        target_entity_id = self.node_entity_store.get_entity_id_for_node_id(
            target_node_id
        )

        if target_entity_id is None:
            return

        if self.last_update_timestamp == encoded_value.timestamp:
            # prevent duplicated updates from also being sent twice
            return

        self.last_update_timestamp = encoded_value.timestamp

        msg = VariableUpdateMessage[VariableDataValueUpdate](
            entity_id=target_entity_id,
            update_content=VariableDataValueUpdate(
                status_code=encoded_value.status_code,
                timestamp=encoded_value.timestamp,
                value=encoded_value.value,
            ),
        )
        msg_funnel.queue_message(msg)
