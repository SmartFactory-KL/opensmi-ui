from enum import StrEnum

from asyncua import ua
from asyncua.common.node import Node
from asyncua.common.subscription import DataChangeEvent

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.json import JsonInModel
from opensmi_ui.opc_model.entities.skill_control_entity import (
    SkillControlEntity,
    SkillControlStateUpdate,
)
from opensmi_ui.opc_model.feature_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
    FeatureSubscribeDataRequest,
    FeatureSubscribeRequest,
)
from opensmi_ui.opc_model.features.lock_feature import GenericAction
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_model.value_read import (
    read_data_change_event_value,
    variant_value_to_string,
)

logger = get_module_logger("opc_model.features.skill_control")


class PossibleSkillControlActions(StrEnum):
    START = "Start"
    HALT = "Halt"
    RESET = "Reset"
    SUSPEND = "Suspend"


class SkillControlAction(JsonInModel):
    requested_action: PossibleSkillControlActions


class SkillControlFeatureNode(FeatureNode):
    _init_step: int
    action_nodes: dict[str, OPCNode]

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self._init_step = 0
        self.entity_type = "SkillControl"

        # save available action nodes
        self.action_nodes = {}
        for child_node in opc_node.children:
            match child_node.browse_name.Name:
                case "Start" | "Halt" | "Reset" | "Suspend":
                    self.action_nodes[child_node.browse_name.Name] = child_node

    def _populate_step(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        match self._init_step:
            case 0:
                self.init_state = FeatureInitState.PENDING

                req = FeatureInitRequest(
                    browse_requests=[], read_requests=[], feature=self
                )

                current_state_node = self.opc_node.get_first_child_node_for_name(
                    "CurrentState"
                )

                req.read_requests.append(
                    ua.ReadValueId(
                        NodeId=current_state_node.node_id,
                        AttributeId=ua.attribute_ids.AttributeIds.Value,
                    )
                )

                self._init_step += 1
                return req
            case 1:
                if last_result is None:
                    raise ValueError(
                        f"Received Unexpected None Result for step {self._init_step}"
                    )

                val = last_result.read_results[0]

                if val.StatusCode is None or val.StatusCode.is_bad():
                    raise ValueError("Failed to read skill state")

                self.opc_node.attributes["Value"] = val.Value
                self.entity = SkillControlEntity(opc_node=self.opc_node, action_nodes=self.action_nodes)

                self._init_step += 1
                self.init_state = FeatureInitState.DONE
                return None
            case _:
                return None

    def _request_subscription(self) -> FeatureSubscribeRequest | None:
        req = FeatureSubscribeRequest(subscriptions=[])

        state_node = self.opc_node.get_first_child_node_for_name("CurrentState")

        req.subscriptions.append(
            FeatureSubscribeDataRequest(
                attr=ua.attribute_ids.AttributeIds.Value,
                feature=self,
                handler=self.on_state_update,
                node_id=state_node.node_id,
            )
        )

        return req

    def on_state_update(self, node: Node, evt: DataChangeEvent):
        if not isinstance(self.entity, SkillControlEntity):
            return

        try:
            value = read_data_change_event_value(evt)
            data_value = evt.data.monitored_item.Value

            if isinstance(value.Value, ua.LocalizedText):
                value = str(value.Value.Text)
            else:
                value = variant_value_to_string(value)

            update = SkillControlStateUpdate(
                entity_id=self.entity_id,
                new_state=value,
                timestamp=data_value.SourceTimestamp,
            )

            self.entity.apply_update(update)
            if self.event_bus is not None:
                self.event_bus.publish(update)

        except Exception:
            logger.exception("Failed to handle Update due to an Exception")
            return

    async def handle_action(self, action: GenericAction) -> None:
        method_node_to_call: OPCNode | None = None
        match action.action_type:
            case "SkillControlAction":
                data = SkillControlAction.model_validate(action.action)
                method_node_to_call = self.action_nodes.get(
                    data.requested_action.value, None
                )
            case _:
                logger.warning(
                    f"received unsupported Action of type {action.action_type} on SkillFeature"
                )
                return

        if method_node_to_call is None:
            raise RuntimeError(
                f"Cannot complete Action {action.action_type} because the desired Node is not present"
            )

        await self.opc_node.ua_node.call_method(methodid=method_node_to_call.node_id)
