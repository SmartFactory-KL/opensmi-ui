from collections import deque
from dataclasses import dataclass

from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.features.variable_feature import VariableFeatureNode
from opensmi_ui.opc_model.model_node import ComponentNode, FeatureNode
from opensmi_ui.opc_model.opc_node import OPCNode

logger = get_module_logger("opc_model.features.variable_container")


@dataclass(frozen=True)
class VariableProcessItem:
    opc_node: OPCNode
    parent_feature: FeatureNode | None


class VariableContainerFeatureNode(FeatureNode):
    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)

        # handle all variables
        vars_to_process = deque(
            [
                VariableProcessItem(opc_node=child_node, parent_feature=None)
                for child_node in opc_node.children
            ]
        )

        variable_features: list[VariableFeatureNode] = []

        while vars_to_process:
            next_item = vars_to_process.popleft()

            ref = next_item.opc_node.reference_type_id

            # only use for components, ignore properties here for now
            if not ref or ref.Identifier != ua.object_ids.ObjectIds.HasComponent:
                continue

            variable_feature = VariableFeatureNode(
                opc_node=next_item.opc_node, parent_component_node=parent_component_node
            )
            variable_feature.entity_type = "VariableFeatureNode"

            if next_item.parent_feature is None:
                variable_features.append(variable_feature)
            else:
                next_item.parent_feature.features.append(variable_feature)

            for child in next_item.opc_node.children:
                vars_to_process.append(
                    VariableProcessItem(opc_node=child, parent_feature=None)
                )

        self.features.extend(variable_features)
