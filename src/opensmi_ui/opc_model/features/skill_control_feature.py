from enum import StrEnum

from asyncua import ua
from asyncua.common.node import Node
from asyncua.common.subscription import DataChangeEvent

from opensmi_ui.event.bus import EventBus
from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.json import JsonInModel
from opensmi_ui.opc_model.entities.skill_state_entity import (
    SkillControlEntity,
    SkillControlStateUpdate,
)
from opensmi_ui.opc_model.features.lock_feature import GenericAction
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
    FeatureSubscribeDataRequest,
    FeatureSubscribeRequest,
)
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_model.value_read import (
    normalize_to_variant,
    variant_value_to_string,
)

logger = get_module_logger("opc_model.features.skill_state")


class PossibleSkillControlActions(StrEnum):
    START = "Start"
    HALT = "Halt"
    RESET = "Reset"
    SUSPEND = "Suspend"


class SkillControlAction(JsonInModel):
    requested_action: PossibleSkillControlActions


class SkillControlFeatureNode(FeatureNode):
    _init_step: int

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

    def subscribe(self) -> FeatureSubscribeRequest | None:
        return None

    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        if self.init_state == FeatureInitState.ERROR:
            return None

        match self._init_step:
            case 0:
                try:
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
                except Exception as e:  # noqa: BLE001 # warning disabled since all errors must lead to error init_state
                    self.init_state = FeatureInitState.ERROR
                    self.init_error = str(e)

                    return None
            case 1:
                try:
                    if last_result is None:
                        raise RuntimeError(
                            f"Received Unexpected None Result for step {self._init_step}"
                        )

                    val = last_result.read_results[0]

                    if val.StatusCode is None or val.StatusCode.is_bad():
                        raise ValueError("Failed to read skill state")

                    self.opc_node.attributes["Value"] = val.Value
                    self.entity = SkillControlEntity(opc_node=self.opc_node)

                    self._init_step += 1
                    self.init_state = FeatureInitState.DONE
                    return None
                except Exception as e:  # noqa: BLE001 # warning disabled since all errors must lead to error init_state
                    self.init_state = FeatureInitState.ERROR
                    self.init_error = str(e)

                    return None
            case _:
                return None

    def request_subscription(
        self, event_bus: EventBus
    ) -> FeatureSubscribeRequest | None:
        self.event_bus = event_bus

        try:
            req = FeatureSubscribeRequest(subscriptions=[])

            state_node = self.opc_node.get_first_child_node_for_name("CurrentState")

            req.subscriptions.append(
                FeatureSubscribeDataRequest(
                    attr=ua.attribute_ids.AttributeIds.Value,
                    handler=self.on_state_update,
                    node_id=state_node.node_id,
                )
            )

            return req
        except KeyError:
            logger.exception("Failed to subscribe to skill state")
            return None

    def on_state_update(self, node: Node, evt: DataChangeEvent):
        if not isinstance(self.entity, SkillControlEntity):
            return

        try:
            data_value = evt.data.monitored_item.Value
            if not isinstance(data_value, ua.DataValue):
                logger.warning(
                    "Received unexpected Non-DataValue Update on SkillStateFeature"
                )
                return

            value = normalize_to_variant(data_value)
            if not isinstance(value, ua.Variant):
                logger.warning("Received unexpected Non-Variant Update on LockFeature")
                return

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
        logger.info("action")
        logger.info(action)

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
