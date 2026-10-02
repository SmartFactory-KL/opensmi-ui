from typing import Protocol

from opensmi_ui.opc_model.node import OPCNode


class MIF(Protocol):
    pass


def create_features_for_node(opc_node: OPCNode):
    match opc_node.browse_name.Name:
        case "Identification":
            return create_identification_feature(opc_node)
        case _:
            raise ValueError(f"Got unknown browse_name {opc_node.browse_name}")


def create_identification_feature(opc_node: OPCNode):
    print(opc_node)
