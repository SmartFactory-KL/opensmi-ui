from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.features.notification_feature import NotificationFeatureNode
from opensmi_ui.opc_model.features.variable_container_feature import (
    VariableContainerFeatureNode,
)
from opensmi_ui.opc_model.model_node import ComponentNode, FeatureNode
from opensmi_ui.opc_model.opc_node import OPCNode

logger = get_module_logger("opc_model.feature")


class FeatureSkippedError(ValueError):
    """Raised whenever a feature could not be created because the node is not a feature and was therefore just skipped."""


class FeatureNotKnownError(ValueError):
    """Raised whenever a BrowseName does not relate to a known Feature"""


def create_feature_for_node(
    opc_node: OPCNode, parent_component_node: ComponentNode
) -> FeatureNode:
    node_name = opc_node.browse_name.Name

    feature: FeatureNode

    match node_name:
        case "Identification" | "ParameterSet" | "Monitoring" | "Attributes":
            feature = VariableContainerFeatureNode(
                opc_node=opc_node, parent_component_node=parent_component_node
            )
        case "Notification":
            feature = NotificationFeatureNode(
                opc_node=opc_node, parent_component_node=parent_component_node
            )

        # case "MachineryBuildingBlocks":
        #     ...
        # case "Resources":
        #     ...
        # case "MethodSet":
        #     ...
        # case "SkillSet":
        #     ...
        # case "Lock":
        #     ...

        # no-ops
        case "Components":
            # already handled, can be skipped
            raise FeatureSkippedError("Components are not Features")

        case _:
            raise FeatureNotKnownError(
                f"Cannot create feature for {opc_node.browse_name.Name}"
            )

    feature.entity_type = type(feature).__name__
    feature.entity = None

    return feature
