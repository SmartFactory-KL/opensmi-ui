from asyncua import ua
from asyncua.common.node import Node
from asyncua.ua.attribute_ids import AttributeIds

from opensmi_ui.api.opc_model_api import get_module_logger

logger = get_module_logger("opc_model.node")

ATTRS_TO_READ = [
    AttributeIds.NodeClass,
    AttributeIds.BrowseName,
    AttributeIds.DisplayName,
]


class OPCNode:
    node_id: ua.NodeId

    node_class: ua.NodeClass
    browse_name: ua.QualifiedName
    display_name: ua.LocalizedText

    _ua_node: Node
    _children: list["OPCNode"]

    def __init__(
        self,
        node_id: ua.NodeId,
        node_class: ua.NodeClass,
        browse_name: ua.QualifiedName,
        display_name: ua.LocalizedText,
        ua_node: Node,
    ) -> None:
        self.node_id = node_id
        self._ua_node = ua_node

        self.node_class = node_class
        self.browse_name = browse_name
        self.display_name = display_name

        self._children = []

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

    def append_child(self, opc_node: "OPCNode"):
        self._children.append(opc_node)

    def get_children(self) -> list["OPCNode"]:
        return self._children

    def __str__(self) -> str:
        return (
            f"OPCNode("
            f"id={self.node_id}, "
            f"class={self.node_class_name}, "
            f"name={self.browse_name!r}"
            f")"
        )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"node_id={self.node_id!r}, "
            f"node_class={self.node_class_name!r}, "
            f"browse_name={self.browse_name!r}, "
            f"display_name={self.display_name!r}"
            f")"
        )
