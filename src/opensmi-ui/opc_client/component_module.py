import logging
import uuid
from typing import TYPE_CHECKING, List

from pyuaadapter.client.base_remote_component import (
    BaseRemoteComponent,
    RemoteComponentSubscriber,
)
from pyuaadapter.client.remote_component_v4 import RemoteComponent as RemoteComponentV4
from pyuaadapter.common.subscription_manager import SubscriptionManager

from messages.message_funnel import MessageFunnel
from model.common_types import GenericActionRequest, GenericActionType
from model.machine_types import (
    ComponentNewMessageUpdate,
    ComponentStateUpdate,
    ComponentUpdateMessage,
    WriteParameterContent,
)
from opc_client.method_module import MethodModule
from opc_client.reference_store import NodeEntityStore, ReferenceStore
from opc_client.remote_variable_module import RemoteVariableModule
from opc_client.skill_module import SkillModule
from util.convert import convert_string_to_variant

if TYPE_CHECKING:
    from opc_client.machine_module import MachineModule
    from opc_client.method_module import MethodModule

logger = logging.getLogger("uvicorn")

msg_funnel = MessageFunnel()


class ComponentModule(RemoteComponentSubscriber):
    remote_component: BaseRemoteComponent

    parent_machine: "MachineModule"
    parent_entity_id: uuid.UUID | None
    parent_node_id_list: List[str]

    entity_id: uuid.UUID

    skills: List[SkillModule]
    methods: List["MethodModule"]
    components: List["ComponentModule"]

    monitoring: List[RemoteVariableModule]
    attributes: List[RemoteVariableModule]
    parameter_set: List[RemoteVariableModule]

    reference_store: ReferenceStore
    node_entity_store: NodeEntityStore

    subscription_manager: SubscriptionManager

    def __init__(
        self,
        input_component: BaseRemoteComponent,
        reference_store: ReferenceStore,
        node_entity_store: NodeEntityStore,
        parent_machine: "MachineModule",
        parent_entity_id: uuid.UUID | None,
        parent_node_id_list: List[str],
        subscription_manager: SubscriptionManager,
    ):
        self.remote_component = input_component
        self.parent_machine = parent_machine

        self.parent_entity_id = parent_entity_id
        self.parent_node_id_list = parent_node_id_list

        self.entity_id = uuid.uuid4()

        self.skills = []
        self.methods = []
        self.components = []

        self.monitoring = []
        self.attributes = []
        self.parameter_set = []

        self.reference_store = reference_store
        self.node_entity_store = node_entity_store

        self.subscription_manager = subscription_manager

        downstream_parent_node_id_list = self.parent_node_id_list.copy()
        downstream_parent_node_id_list.append(
            self.remote_component._ua_node.nodeid.to_string()
        )

        if isinstance(self.remote_component, RemoteComponentV4):
            for _method in self.remote_component.method_set.values():
                self.methods.append(
                    MethodModule(
                        input_method=_method,
                        reference_store=reference_store,
                        node_entity_store=node_entity_store,
                        parent_machine=self.parent_machine,
                        parent_entity_id=self.entity_id,
                        parent_node_id_list=downstream_parent_node_id_list,
                        subscription_manager=self.subscription_manager,
                    )
                )

        for _skill in self.remote_component.skill_set.values():
            self.skills.append(
                SkillModule(
                    input_skill=_skill,
                    reference_store=reference_store,
                    node_entity_store=node_entity_store,
                    parent_machine=self.parent_machine,
                    parent_entity_id=self.entity_id,
                    parent_node_id_list=downstream_parent_node_id_list,
                    subscription_manager=self.subscription_manager,
                )
            )

        for _skill in self.remote_component.feasibility_check_set.values():
            self.skills.append(
                SkillModule(
                    input_skill=_skill,
                    reference_store=reference_store,
                    node_entity_store=node_entity_store,
                    parent_machine=self.parent_machine,
                    parent_entity_id=self.entity_id,
                    parent_node_id_list=downstream_parent_node_id_list,
                    subscription_manager=self.subscription_manager,
                )
            )

        for _skill in self.remote_component.precondition_check_set.values():
            self.skills.append(
                SkillModule(
                    input_skill=_skill,
                    reference_store=reference_store,
                    node_entity_store=node_entity_store,
                    parent_machine=self.parent_machine,
                    parent_entity_id=self.entity_id,
                    parent_node_id_list=downstream_parent_node_id_list,
                    subscription_manager=self.subscription_manager,
                )
            )

        for _parameter in self.remote_component.components.values():
            self.components.append(
                ComponentModule(
                    input_component=_parameter,
                    reference_store=reference_store,
                    node_entity_store=node_entity_store,
                    parent_machine=self.parent_machine,
                    parent_entity_id=self.entity_id,
                    parent_node_id_list=downstream_parent_node_id_list,
                    subscription_manager=self.subscription_manager,
                )
            )

        for _monitoring in self.remote_component.monitoring.values():
            self.monitoring.append(
                RemoteVariableModule(
                    input_remote_variable=_monitoring,
                    reference_store=reference_store,
                    node_entity_store=node_entity_store,
                    parent_entity_id=self.entity_id,
                    subscription_manager=self.subscription_manager,
                )
            )

        for _attribute in self.remote_component.attributes.values():
            self.attributes.append(
                RemoteVariableModule(
                    input_remote_variable=_attribute,
                    reference_store=reference_store,
                    node_entity_store=node_entity_store,
                    parent_entity_id=self.entity_id,
                    subscription_manager=self.subscription_manager,
                )
            )

        for _parameter in self.remote_component.parameter_set.values():
            self.parameter_set.append(
                RemoteVariableModule(
                    input_remote_variable=_parameter,
                    reference_store=reference_store,
                    node_entity_store=node_entity_store,
                    parent_entity_id=self.entity_id,
                    subscription_manager=self.subscription_manager,
                )
            )

        self.remote_component.add_subscriber(self)
        self.reference_store.add_component(self)
        self.node_entity_store.add_node_entity_reference(
            self.remote_component._ua_node.nodeid.to_string(), self.entity_id
        )

    async def to_dto(self):
        basic_dto = self.remote_component.dto()

        data = {
            "name": basic_dto["name"],
            "entity_id": self.entity_id,
            "node_id": basic_dto["node_id"],
            "type": basic_dto["type"],
            "current_state": basic_dto["current_state"],
            "skill_set": [await s.to_dto() for s in self.skills],
            "methods": [await m.to_dto() for m in self.methods],
            "components": [await c.to_dto() for c in self.components],
            "monitoring": [await m.to_dto() for m in self.monitoring],
            "attributes": [await a.to_dto() for a in self.attributes],
            "parameter_set": [await p.to_dto() for p in self.parameter_set],
            "parent_entity_id": self.parent_entity_id,
            "parent_node_id_list": self.parent_node_id_list,
        }
        return data

    def on_server_disconnect(self):
        for _component in self.components:
            _component.on_server_disconnect()

        try:
            self.remote_component._subscribers.remove(self)
        except Exception as _:
            logger.info("No Component Subscriber, nothing to remove")

    async def apply_component_action(self, action: GenericActionRequest):
        self.parent_machine.tick_lock_auto_free()

        match action.action_type:
            case GenericActionType.WriteParameter:
                action_content = WriteParameterContent.model_validate(
                    action.action_content
                )
                logger.info("Requested Parameter Single Write")
                logger.info(action_content)

                parameter = self.remote_component.parameter_set.get(
                    action_content.parameter_name
                )
                # logger.info(type(parameter.value))

                # UPDATE - no longer needed, will be inferred from python type of value instead
                data_type = await parameter.ua_node.read_data_type_as_variant_type()
                # Try to parse the string input into the needed format based on Variant

                logger.info(
                    f"Try to convert {action_content.parameter_new_value} to VariantType {data_type.name} using value_type {type(parameter.value)}"
                )

                val = convert_string_to_variant(
                    action_content.parameter_new_value,
                    data_type.value,
                    type(parameter.value),
                )

                await parameter.write_value(val)
            case _:
                raise Exception("Invalid action for a Component: " + action.action_type)

    ## Subscriber Stuff
    ## -------------------------------------
    def on_state_change(self, new_state):
        msg = ComponentUpdateMessage[ComponentStateUpdate](
            entity_id=self.entity_id,
            update_content=ComponentStateUpdate(new_state=new_state),
        )
        msg_funnel.queue_message(msg)

    def on_new_message(self, component, text, severity, code):
        msg = ComponentUpdateMessage[ComponentNewMessageUpdate](
            entity_id=self.entity_id,
            update_content=ComponentNewMessageUpdate(
                severity=severity, code=code, text=text
            ),
        )
        msg_funnel.queue_message(msg)

    def on_monitoring_update(self, var):
        self.on_variable_update(var)

    def on_parameter_update(self, var):
        self.on_variable_update(var)

    def on_variable_update(self, var):
        pass
        # encoded_value = encode_value_for_type(var.value, var._ua_data_type)
        # target_node_id = var.ua_node.nodeid.to_string()
        # target_entity_id = self.node_entity_store.get_entity_id_for_node_id(
        #     target_node_id
        # )

        # if target_entity_id is not None:
        #     msg = VariableUpdateMessage[VariableValueUpdate](
        #         entity_id=target_entity_id,
        #         update_content=VariableValueUpdate(
        #             value=convert_value_to_simple(encoded_value),
        #             timestamp=var.timestamp.isoformat(),
        #         ),
        #     )
        #     msg_funnel.queue_message(msg)
