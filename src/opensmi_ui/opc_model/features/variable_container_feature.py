from collections import deque
from dataclasses import dataclass

from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.variable_container_entity import (
    VariableContainerEntity,
)
from opensmi_ui.opc_model.feature_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
)
from opensmi_ui.opc_model.features.variable_feature import VariableFeatureNode
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_session.namespace import OPCNamespace

logger = get_module_logger("opc_model.features.variable_container")


@dataclass(frozen=True)
class VariableProcessItem:
    opc_node: OPCNode
    parent_feature: FeatureNode | None


class VariableContainerFeatureNode(FeatureNode):
    def __init__(
        self,
        opc_node: OPCNode,
        opc_namespace: OPCNamespace,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(
            opc_node=opc_node,
            opc_namespace=opc_namespace,
            parent_component_node=parent_component_node,
            parent_feature_node=parent_feature_node,
        )
        self.entity_type = "VariableContainer"

        # handle all variables
        vars_to_process = deque(
            [
                VariableProcessItem(opc_node=child_node, parent_feature=self)
                for child_node in opc_node.children
            ]
        )

        variable_features: list[VariableFeatureNode] = []

        while vars_to_process:
            next_item = vars_to_process.popleft()

            ref = next_item.opc_node.reference_type

            # only use for components, ignore properties here for now
            if not ref or ref.Identifier != ua.object_ids.ObjectIds.HasComponent:
                if ref is not None:
                    logger.debug(
                        f"Found Node without HasComponent: Ref Type is {ua.object_ids.ObjectIdNames.get(ref.Identifier, 'unknown')} for NodeId {next_item.opc_node.node_id.NamespaceIndex} : {next_item.opc_node.node_id.Identifier}"
                    )
                continue

            variable_feature = VariableFeatureNode(
                opc_node=next_item.opc_node,
                opc_namespace=opc_namespace,
                parent_component_node=parent_component_node,
                parent_feature_node=next_item.parent_feature,
            )

            if next_item.parent_feature is None:
                variable_features.append(variable_feature)
            else:
                next_item.parent_feature.features.append(variable_feature)

            for child in next_item.opc_node.children:
                vars_to_process.append(
                    VariableProcessItem(opc_node=child, parent_feature=None)
                )

        self.features.extend(variable_features)

    def _populate_step(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        self.entity = VariableContainerEntity(opc_node=self.opc_node)
        self.init_state = FeatureInitState.DONE
        return None
