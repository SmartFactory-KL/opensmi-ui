from collections import deque

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.feature.identification import IdentificationFeature
from opensmi_ui.opc_model.model import ComponentTree, MIFContainer, MIFeature
from opensmi_ui.opc_model.node import OPCNode

logger = get_module_logger("mif_factory")


def add_containers_to_component_tree(component_tree: ComponentTree) -> ComponentTree:
    components_to_process = deque[ComponentTree]([component_tree])

    while components_to_process:
        next_item = components_to_process.popleft()

        mifco = create_feature_container(next_item.node)
        next_item.mifco = mifco

        for child in next_item.children:
            components_to_process.append(child)

    return component_tree


def create_feature_container(opc_node: OPCNode) -> MIFContainer:
    container = MIFContainer(opc_node=opc_node)

    for child in opc_node.get_children():
        feature = create_feature_for_node(child)
        if feature is not None:
            container.add_feature(feature)

    return container


def create_feature_for_node(opc_node: OPCNode) -> MIFeature | None:
    match opc_node.browse_name.Name:
        case "Identification":
            return IdentificationFeature(opc_node=opc_node)
        case _:
            return None
