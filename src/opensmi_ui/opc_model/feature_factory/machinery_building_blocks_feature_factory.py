from opensmi_ui.opc_model.features.machinery_item_state_feature import (
    MachineryItemStateFeatureNode,
)
from opensmi_ui.opc_model.features.user_container_feature import (
    UserContainerFeatureNode,
)
from opensmi_ui.opc_model.feature_node import ComponentNode, FeatureNode
from opensmi_ui.opc_model.opc_node import OPCNode


def create_machinery_building_block_features(
    opc_node: OPCNode,
    parent_component_node: ComponentNode,
    parent_feature_node: FeatureNode | None = None,
) -> list[FeatureNode]:
    feature_list: list[FeatureNode] = []

    for child in opc_node.children:
        match child.browse_name.Name:
            case "MachineryItemState":
                feature_list.append(
                    MachineryItemStateFeatureNode(
                        opc_node=child,
                        parent_component_node=parent_component_node,
                        parent_feature_node=parent_feature_node,
                    )
                )
            case "MachineryOperationMode":
                ...
            case "Users":
                feature_list.append(
                    UserContainerFeatureNode(
                        opc_node=child,
                        parent_component_node=parent_component_node,
                        parent_feature_node=parent_feature_node,
                    )
                )
            case _:
                print(f"unkown block: {child.browse_name.Name}")

    return feature_list
