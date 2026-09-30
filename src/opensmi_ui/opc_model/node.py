from asyncua import ua
from asyncua.common.node import Node
from asyncua.ua.attribute_ids import AttributeIds

from opensmi_ui.api.opc_model_api import get_module_logger
from opensmi_ui.api.opc_session_api import OPCSession

logger = get_module_logger("opc_model.node")


class OPCNode:
    node_id: ua.NodeId
    node_class: ua.NodeClass
    browse_name: ua.QualifiedName
    display_name: ua.LocalizedText
    description: ua.LocalizedText | None

    _ua_node: Node

    def __init__(
        self,
        node_id: ua.NodeId,
        node_class: ua.NodeClass,
        browse_name: ua.QualifiedName,
        display_name: ua.LocalizedText,
        description: ua.LocalizedText | None,
        ua_node: Node,
    ) -> None:
        self.node_id = node_id
        self.node_class = node_class
        self.browse_name = browse_name
        self.display_name = display_name
        self.description = description
        self._ua_node = ua_node

    @property
    def is_object(self) -> bool:
        return self.node_class == ua.NodeClass.Object

    @property
    def is_variable(self) -> bool:
        return self.node_class == ua.NodeClass.Variable

    @property
    def is_method(self) -> bool:
        return self.node_class == ua.NodeClass.Method

    @property
    def node_class_name(self) -> str:
        return self.node_class.name

    def ua_node(self) -> Node:
        return self._ua_node


async def create_opc_node(
    opc_session: OPCSession,
    node_id: ua.NodeId,
) -> OPCNode:
    node = opc_session.opc_client.get_node(node_id)

    node_attrs = await node.read_attributes(
        [
            AttributeIds.NodeClass,
            AttributeIds.BrowseName,
            AttributeIds.DisplayName,
            AttributeIds.Description,
        ]
    )

    for attr in node_attrs:
        if attr.Value is None:
            raise ValueError(f"Node {node_id} is missing an attribute value")

    return OPCNode(
        node_id=node.nodeid,
        node_class=ua.NodeClass(node_attrs[0].Value.Value),
        browse_name=node_attrs[1].Value.Value,
        display_name=node_attrs[2].Value.Value,
        description=node_attrs[3].Value.Value,
        ua_node=node,
    )
