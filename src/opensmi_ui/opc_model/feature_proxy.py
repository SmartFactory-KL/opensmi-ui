from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.feature_factory.machinery_building_blocks_feature_factory import (
    create_machinery_building_block_features,
)
from opensmi_ui.opc_model.features.lock_feature import LockFeatureNode
from opensmi_ui.opc_model.features.method_container_feature import (
    MethodContainerFeatureNode,
)
from opensmi_ui.opc_model.features.notification_feature import NotificationFeatureNode
from opensmi_ui.opc_model.features.resource_container_feature import (
    ResourceContainerFeatureNode,
)
from opensmi_ui.opc_model.features.skill_group_container_feature import (
    SkillGroupContainerFeatureNode,
)
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


def create_features_for_node(
    opc_node: OPCNode, parent_component_node: ComponentNode
) -> list[FeatureNode]:
    node_name = opc_node.browse_name.Name

    feature_list: list[FeatureNode]

    match node_name:
        case (
            "Identification"
            | "ParameterSet"
            | "Monitoring"
            | "Attributes"
            | "FinalResultData"
        ):
            feature_list = [
                VariableContainerFeatureNode(
                    opc_node=opc_node, parent_component_node=parent_component_node
                )
            ]
        case "Notification":
            feature_list = [
                NotificationFeatureNode(
                    opc_node=opc_node, parent_component_node=parent_component_node
                )
            ]
        case "Lock":
            feature_list = [
                LockFeatureNode(
                    opc_node=opc_node, parent_component_node=parent_component_node
                )
            ]
        case "Resources":
            feature_list = [
                ResourceContainerFeatureNode(
                    opc_node=opc_node, parent_component_node=parent_component_node
                )
            ]
        case "MachineryBuildingBlocks":
            feature_list = create_machinery_building_block_features(
                opc_node=opc_node, parent_component_node=parent_component_node
            )

        case "MethodSet":
            feature_list = [
                MethodContainerFeatureNode(
                    opc_node=opc_node, parent_component_node=parent_component_node
                )
            ]
        case "SkillSet":
            feature_list = [
                SkillGroupContainerFeatureNode(
                    opc_node=opc_node, parent_component_node=parent_component_node
                )
            ]

        # no-ops
        case "Components":
            # already handled, can be skipped
            raise FeatureSkippedError("Components are not Features")

        case _:
            raise FeatureNotKnownError(
                f"Cannot create feature for {opc_node.browse_name.Name}"
            )

    return feature_list
