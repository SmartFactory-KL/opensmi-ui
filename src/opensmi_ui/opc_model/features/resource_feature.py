from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.resource_container_entity import (
    ResourceContainerEntity,
)
from opensmi_ui.opc_model.features.variable_container_feature import (
    VariableContainerFeatureNode,
)
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
)
from opensmi_ui.opc_model.opc_node import OPCNode

logger = get_module_logger("opc_model.features.resource")


class ResourceFeatureNode(FeatureNode):
    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self.entity_type = "Resource"

        # add variables
        for child in opc_node.children:
            ref = child.reference_type_id

            if not ref or ref.Identifier != ua.object_ids.ObjectIds.HasComponent:
                continue

            variable_container_feature = VariableContainerFeatureNode(
                opc_node=child,
                parent_component_node=parent_component_node,
                parent_feature_node=self,
            )

            self.features.append(variable_container_feature)

    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        self.entity = ResourceContainerEntity(opc_node=self.opc_node)
        self.init_state = FeatureInitState.DONE

        return None
