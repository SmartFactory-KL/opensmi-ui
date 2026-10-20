from collections.abc import Mapping
from typing import Any

from asyncua import ua
from asyncua.common.node import Node

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.common import JsonOutModel
from opensmi_ui.opc_model.opc_types import (
    LocalizedTextData,
    NodeIdData,
    QualifiedNameData,
)

logger = get_module_logger("opc_model.node")


class OPCNodeData(JsonOutModel):
    node_id: NodeIdData
    node_class: str
    browse_name: QualifiedNameData
    display_name: LocalizedTextData
    type_definition_id: NodeIdData | None
    reference_type_id: NodeIdData | None
    attributes: Mapping[str, str]
    properties: Mapping[str, str]


class OPCNode:
    node_id: ua.NodeId

    node_class: ua.NodeClass
    browse_name: ua.QualifiedName
    display_name: ua.LocalizedText

    ua_node: Node

    type_definition_id: ua.NodeId | None = None
    reference_type_id: ua.NodeId | None = None

    attributes: dict[str, Any]
    properties: dict[str, Any]

    children: list["OPCNode"]

    def __init__(
        self,
        node_id: ua.NodeId,
        node_class: ua.NodeClass,
        browse_name: ua.QualifiedName,
        display_name: ua.LocalizedText,
        ua_node: Node,
        type_definition_id: ua.NodeId | None = None,
        reference_type_id: ua.NodeId | None = None,
        attributes: dict[str, Any] | None = None,
        properties: dict[str, Any] | None = None,
    ) -> None:
        self.node_id = node_id
        self.node_class = node_class
        self.browse_name = browse_name
        self.display_name = display_name

        self.ua_node = ua_node

        self.type_definition_id = type_definition_id
        self.reference_type_id = reference_type_id

        self.attributes = attributes if attributes is not None else {}
        self.properties = properties if properties is not None else {}

        self.children = []

    @property
    def node_class_name(self) -> str:
        return self.node_class.name

    def append_child(self, opc_node: "OPCNode"):
        self.children.append(opc_node)

    def get_first_child_node_for_name(self, name: str) -> "OPCNode":
        """Raises KeyError if no child node was found with matching name"""
        # TODO: Think about how to handle namespacing cleanly
        # TODO: and check if a node can have multiple children with the same
        # TODO: BrowseName.Name while having different BrowseName.NamespaceIndex values
        for child in self.children:
            if child.browse_name.Name == name:
                return child

        raise KeyError(f"No Child Node found for Name {name}")

    def get_children(self) -> list["OPCNode"]:
        return self.children

    def get_data(self) -> OPCNodeData:
        return OPCNodeData(
            node_id=NodeIdData.from_ua(self.node_id),
            node_class=self.node_class_name,
            browse_name=QualifiedNameData.from_ua(self.browse_name),
            display_name=LocalizedTextData.from_ua(self.display_name),
            attributes={
                attr_key: str(attr_value)
                for attr_key, attr_value in self.attributes.items()
            },
            properties={
                prop_key: str(prop_value)
                for prop_key, prop_value in self.properties.items()
            },
            reference_type_id=NodeIdData.from_ua(self.reference_type_id)
            if self.reference_type_id is not None
            else None,
            type_definition_id=NodeIdData.from_ua(self.type_definition_id)
            if self.type_definition_id is not None
            else None,
        )

    def __str__(self) -> str:
        return f"{self.node_class_name} '{self.browse_name}' ({self.node_id})"

    def __repr__(self) -> str:
        fields = [
            f"node_id={self.node_id!r}",
            f"node_class={self.node_class.name}",
            f"browse_name={self.browse_name!r}",
            f"display_name={self.display_name!r}",
        ]

        if self.reference_type_id is not None:
            fields.append(f"reference_type_id={self.reference_type_id!r}")

        if self.type_definition_id is not None:
            fields.append(f"type_definition_id={self.type_definition_id!r}")

        if self.attributes:
            fields.append(f"attributes={self.attributes!r}")

        if self.properties:
            fields.append(f"properties={self.properties!r}")

        if self.children:
            fields.append(f"children_count={len(self.children)}")

        return f"{type(self).__name__}({', '.join(fields)})"
