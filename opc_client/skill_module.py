import logging
import uuid
from typing import TYPE_CHECKING, List

from pyuaadapter.client.base_remote_callable import RemoteSkillSubscriber
from pyuaadapter.client.base_remote_skill import BaseRemoteSkill
from pyuaadapter.client.remote_variable import RemoteVariable
from pyuaadapter.common.subscription_manager import SubscriptionManager

from messages.message_funnel import MessageFunnel
from model.common_types import GenericActionRequest, GenericActionType
from model.machine_types import (
    SkillStateUpdate,
    SkillUpdateMessage,
    WriteParameterContent,
)
from model.node_types import SkillDto
from opc_client.reference_store import NodeEntityStore, ReferenceStore
from opc_client.remote_variable_module import RemoteVariableModule
from util.convert import convert_string_to_variant

if TYPE_CHECKING:
    from opc_client.machine_module import MachineModule

logger = logging.getLogger("uvicorn")

msg_funnel = MessageFunnel()


class SkillModule(RemoteSkillSubscriber):
    remote_skill: BaseRemoteSkill
    entity_id: uuid.UUID

    parent_machine: "MachineModule"
    parent_entity_id: uuid.UUID | None
    parent_node_id_list: List[str]

    monitoring: List[RemoteVariableModule]
    parameter_set: List[RemoteVariableModule]
    final_result_data: List[RemoteVariableModule]

    reference_store: ReferenceStore
    node_entity_store: NodeEntityStore

    subscription_manager: SubscriptionManager

    def __init__(
        self,
        input_skill: BaseRemoteSkill,
        reference_store: ReferenceStore,
        node_entity_store: NodeEntityStore,
        parent_machine: "MachineModule",
        parent_entity_id: uuid.UUID | None,
        parent_node_id_list: List[str],
        subscription_manager: SubscriptionManager,
    ):
        self.remote_skill = input_skill
        self.entity_id = uuid.uuid4()
        self.parent_machine = parent_machine

        self.parent_entity_id = parent_entity_id
        self.parent_node_id_list = parent_node_id_list

        self.monitoring = []
        self.parameter_set = []
        self.final_result_data = []

        self.reference_store = reference_store
        self.node_entity_store = node_entity_store

        self.subscription_manager = subscription_manager

        for _monitoring in self.remote_skill.monitoring.values():
            self.monitoring.append(
                RemoteVariableModule(
                    input_remote_variable=_monitoring,
                    reference_store=reference_store,
                    node_entity_store=node_entity_store,
                    parent_entity_id=self.entity_id,
                    subscription_manager=self.subscription_manager,
                )
            )

        for _parameter in self.remote_skill.parameter_set.values():
            self.parameter_set.append(
                RemoteVariableModule(
                    input_remote_variable=_parameter,
                    reference_store=reference_store,
                    node_entity_store=node_entity_store,
                    parent_entity_id=self.entity_id,
                    subscription_manager=self.subscription_manager,
                )
            )

        for _final_result in self.remote_skill.final_result_data.values():
            self.final_result_data.append(
                RemoteVariableModule(
                    input_remote_variable=_final_result,
                    reference_store=reference_store,
                    node_entity_store=node_entity_store,
                    parent_entity_id=self.entity_id,
                    subscription_manager=self.subscription_manager,
                )
            )

        self.remote_skill.add_subscriber(self)
        self.reference_store.add_skill(self)
        self.node_entity_store.add_node_entity_reference(
            self.remote_skill.ua_base_node.nodeid.to_string(), self.entity_id
        )

    async def to_dto(self) -> SkillDto:
        basic_dto = self.remote_skill.dto()
        return SkillDto(
            name=basic_dto["name"],
            entity_id=self.entity_id,
            node_id=basic_dto["node_id"],
            type=basic_dto["type"],
            current_state=basic_dto["current_state"],
            depends_on=[
                n.to_string().replace('"', "")
                for n in self.remote_skill.depends_on.keys()
            ],
            dependency_of=[
                n.to_string().replace('"', "")
                for n in self.remote_skill.dependency_of.keys()
            ],
            parameter_set=[await v.to_dto() for v in self.parameter_set],
            monitoring=[await v.to_dto() for v in self.monitoring],
            final_result_data=[await v.to_dto() for v in self.final_result_data],
            parent_entity_id=self.parent_entity_id,
            min_access_level=basic_dto["min_access_level"],
            is_suspendable=self.remote_skill.suspendable,
            parent_node_id_list=self.parent_node_id_list,
        )

    async def apply_skill_action(self, skill_action: GenericActionRequest):
        self.parent_machine.tick_lock_auto_free()

        match skill_action.action_type:
            case GenericActionType.WriteParameter:
                action_content = WriteParameterContent.model_validate(
                    skill_action.action_content
                )
                logger.info("Requested Parameter Single Write")
                logger.info(action_content)

                parameter = self.remote_skill.parameter_set.get(
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

            case GenericActionType.WriteParameterList:
                logger.info("Requested Parameter List Write")
                raise Exception("Not implemented yet")

            case GenericActionType.SkillStart:
                await self.remote_skill.start()

            case GenericActionType.SkillHalt:
                await self.remote_skill.halt()

            case GenericActionType.SkillReset:
                await self.remote_skill.reset()

            case GenericActionType.SkillSuspend:
                await self.remote_skill.suspend()

    def on_server_disconnect(self):
        try:
            self.remote_skill._subscribers.remove(self)
        except Exception as _:
            logger.info("No Skill Subscriber, nothing to remove")

    ## Subscriber Stuff
    ## -------------------------------------

    def on_skill_state_change(self, new_state):
        msg = SkillUpdateMessage[SkillStateUpdate](
            entity_id=self.entity_id,
            update_content=SkillStateUpdate(new_state=new_state.name),
        )
        msg_funnel.queue_message(msg)

    def on_final_result_update(self, var: RemoteVariable):
        self.on_variable_update(var)

    def on_monitoring_update(self, var):
        self.on_variable_update(var)

    def on_parameter_update(self, var):
        self.on_variable_update(var)

    def on_variable_update(self, var):
        # disabled in favor of using datachange_notifications directly for RemoteVariable
        pass
        # encoded_value = encode_value_fo r_type(var.value, var._ua_data_type)
        # encoded_value = serialize_data_value(var.value, var._ua_data_type)

        # target_node_id = var.ua_node.nodeid.to_string()
        # target_entity_id = self.node_entity_store.get_entity_id_for_node_id(
        #     target_node_id
        # )

        # if target_entity_id is not None:
        #     msg = VariableUpdateMessage[VariableValueUpdate](
        #         entity_id=target_entity_id,
        #         update_content=VariableValueUpdate(
        #             # value=convert_value_to_simple(encoded_value),
        #             value=(encoded_value),
        #             timestamp=var.timestamp.isoformat(),
        #         ),
        #     )
        #     msg_funnel.queue_message(msg)
