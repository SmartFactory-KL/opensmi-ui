from asyncua import ua
from asyncua.common.node import Node
from asyncua.ua.attribute_ids import AttributeIds

from opensmi_ui.api.opc_model_api import get_module_logger
from opensmi_ui.api.opc_session_api import OPCSession

logger = get_module_logger("opc_model.node")

ATTRS_TO_READ = [
    AttributeIds.NodeClass,
    AttributeIds.BrowseName,
    AttributeIds.DisplayName,
    AttributeIds.Description,
]


class OPCNode:
    node_id: ua.NodeId
    node_attrs: dict[AttributeIds, ua.DataValue]

    node_class: ua.NodeClass
    browse_name: str
    display_name: str
    description: str | None

    _ua_node: Node

    def __init__(
        self,
        node_id: ua.NodeId,
        node_attrs: dict[AttributeIds, ua.DataValue],
        ua_node: Node,
    ) -> None:
        self.node_id = node_id
        self._ua_node = ua_node

        for attr_to_read in ATTRS_TO_READ:
            match attr_to_read:
                case AttributeIds.NodeClass:
                    val = node_attrs[AttributeIds.NodeClass]
                    if val.Value is None:
                        raise ValueError("invalid None value for NodeClass")
                    self.node_class = ua.NodeClass(val.Value.Value)
                    break
                case AttributeIds.BrowseName:
                    val = node_attrs[AttributeIds.BrowseName]
                    if val.Value is None:
                        raise ValueError("invalid None value for BrowseName")
                    self.browse_name = str(val.Value.Value)
                    break
                case AttributeIds.DisplayName:
                    val = node_attrs[AttributeIds.DisplayName]
                    if val.Value is None:
                        raise ValueError("invalid None value for DisplayName")
                    self.display_name = str(val.Value.Value)
                    break
                case AttributeIds.Description:
                    val = node_attrs[AttributeIds.Description]
                    if val.Value is None:
                        self.description = None
                    else:
                        self.description = str(val.Value.Value)
                    break
                case _:
                    raise ValueError("received unwanted attribute")

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

    node_attrs = await node.read_attributes(ATTRS_TO_READ)
    node_attrs_dict = dict(zip(ATTRS_TO_READ, node_attrs, strict=True))

    return OPCNode(
        node_id=node.nodeid,
        node_attrs=node_attrs_dict,
        ua_node=node,
    )
