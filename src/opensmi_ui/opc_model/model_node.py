import uuid
from abc import abstractmethod
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Union

from asyncua import ua
from asyncua.common.events import Event
from asyncua.common.node import Node
from asyncua.common.subscription import DataChangeNotif
from asyncua.ua.attribute_ids import AttributeIds

from opensmi_ui.model.common import JsonOutModel
from opensmi_ui.opc_model.entities.component_entity import ComponentEntity
from opensmi_ui.opc_model.entities.entity import FeatureNodeEntity
from opensmi_ui.opc_model.opc_node import OPCNode, OPCNodeData


@dataclass
class FeatureInitRequest:
    read_requests: list[ua.ReadValueId]
    browse_requests: list[ua.BrowseDescription]

    feature: "FeatureNode"


@dataclass
class FeatureInitResult:
    read_results: list[ua.DataValue]
    browse_results: list[ua.BrowseResult]


@dataclass
class FeatureSubscribeDataRequest:
    node: Node
    attr: AttributeIds

    handler: Callable[[Node, Any, DataChangeNotif], None]


@dataclass
class FeatureSubscribeEventRequest:
    node: Node
    attr: AttributeIds

    handler: Callable[[Event], None]


@dataclass
class FeatureSubscribeRequest:
    subscriptions: list[FeatureSubscribeDataRequest | FeatureSubscribeEventRequest]


class EntityNodeData(JsonOutModel):
    opc_node: OPCNodeData

    entity: Any | None
    entity_id: uuid.UUID
    entity_type: str | None


class FeatureNodeData(EntityNodeData):
    features: list["FeatureNodeData"]


class FeatureNode:
    opc_node: OPCNode

    parent_component_node: "ComponentNode"
    parent_feature_node: Union["FeatureNode", None]

    entity: FeatureNodeEntity | None
    entity_id: uuid.UUID
    entity_type: str | None

    features: list["FeatureNode"]

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: "ComponentNode",
        parent_feature_node: Union["FeatureNode", None] = None,
    ):
        self.opc_node = opc_node
        self.entity = None
        self.entity_id = uuid.uuid4()
        self.entity_type = None

        self.parent_component_node = parent_component_node
        self.parent_feature_node = parent_feature_node

        self.features = []

    @abstractmethod
    def subscribe(self) -> FeatureSubscribeRequest | None:
        """subscribe() is called to gather all subscription requests. Returning None means no subscriptions are requested."""
        return None

    @abstractmethod
    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        """advance() is called by the model until no further requests are present. The initial last_result will contain empty lists."""
        return None

    def get_data(self) -> FeatureNodeData:
        return FeatureNodeData(
            opc_node=self.opc_node.get_data(),
            entity=self.entity.get_data() if self.entity is not None else None,
            entity_id=self.entity_id,
            entity_type=self.entity_type if self.entity_type is not None else None,
            features=[feat.get_data() for feat in self.features],
        )


class ComponentNodeData(EntityNodeData):
    features: list[FeatureNodeData]
    children: list["ComponentNodeData"]


class ComponentNode:
    opc_node: OPCNode

    entity: ComponentEntity | None
    entity_id: uuid.UUID
    entity_type: str | None

    parent_component_node: Union["ComponentNode", None]

    features: list[FeatureNode]

    children: list["ComponentNode"]

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: Union["ComponentNode", None] = None,
    ):
        self.opc_node = opc_node
        self.entity = None
        self.entity_id = uuid.uuid4()
        self.entity_type = None

        self.parent_component_node = parent_component_node

        self.features = []
        self.children = []

    def get_data(self) -> ComponentNodeData:
        return ComponentNodeData(
            opc_node=self.opc_node.get_data(),
            entity=self.entity.get_data() if self.entity is not None else None,
            entity_id=self.entity_id,
            entity_type=self.entity_type if self.entity_type is not None else None,
            features=[feat.get_data() for feat in self.features],
            children=[child.get_data() for child in self.children],
        )


def print_component_trees(trees: list[ComponentNode]) -> None:
    """Print component trees in a human-readable tree format."""

    def print_tree(tree: ComponentNode, prefix: str = "", is_last: bool = True) -> None:
        name = tree.opc_node.browse_name.Name
        child_count = len(tree.opc_node.get_children())

        branch = "└── " if is_last else "├── "
        print(f"{prefix}{branch}{name}[{child_count}]")

        for feature in tree.opc_node.get_children():
            print(f"{prefix}    +{feature.display_name.Text}")

        prefix += "    "

        for i, child in enumerate(tree.children):
            print_tree(
                child,
                prefix,
                is_last=(i == len(tree.children) - 1),
            )

    for i, tree in enumerate(trees):
        print_tree(
            tree,
            is_last=(i == len(trees) - 1),
        )


def visit_tree_features(
    tree: ComponentNode, method: Callable[[FeatureNode, ComponentNode], None]
) -> None:
    """This method can be used to simply visit all features within a tree.
    The visitor method receives the current feature as well as its parent component."""
    components_to_process = deque([tree])
    while components_to_process:
        next_component = components_to_process.popleft()

        # features are trees as well, collect them
        features_to_process = deque(next_component.features)
        while features_to_process:
            next_feature = features_to_process.popleft()

            method(next_feature, next_component)

            for child_feature in next_feature.features:
                features_to_process.append(child_feature)

        for child in next_component.children:
            components_to_process.append(child)
