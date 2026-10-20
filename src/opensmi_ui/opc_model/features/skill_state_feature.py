from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.skill_state_entity import SkillStateEntity
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
    FeatureSubscribeRequest,
)
from opensmi_ui.opc_model.opc_node import OPCNode

logger = get_module_logger("opc_model.features.skill_state")


class SkillStateFeatureNode(FeatureNode):
    _init_step: int

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self._init_step = 0
        self.entity_type = "SkillState"

        # create features
        for child in opc_node.children:
            ...

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
                    self.entity = SkillStateEntity(opc_node=self.opc_node)

                    self._init_step += 1
                    self.init_state = FeatureInitState.DONE
                    return None
                except Exception as e:  # noqa: BLE001 # warning disabled since all errors must lead to error init_state
                    self.init_state = FeatureInitState.ERROR
                    self.init_error = str(e)

                    return None
            case _:
                return None
