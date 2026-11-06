import uuid
from abc import abstractmethod
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Union

from asyncua import ua
from asyncua.common.events import Event
from asyncua.common.node import Node
from asyncua.common.subscription import DataChangeEvent
from asyncua.ua.attribute_ids import AttributeIds

from opensmi_ui.event.bus import EventBus
from opensmi_ui.model.action import GenericAction
from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.entities.component_entity import ComponentEntity
from opensmi_ui.opc_model.entities.entity import FeatureNodeEntity
from opensmi_ui.opc_model.opc_node import OPCNode, OPCNodeData
from opensmi_ui.opc_session.namespace import OPCNamespace


@dataclass
class FeatureInitRequest:
    read_requests: list[ua.ReadValueId]
    browse_requests: list[ua.BrowseDescription]

    feature: "FeatureNode"


@dataclass
class FeatureInitResult:
    read_results: list[ua.DataValue]
    browse_results: list[ua.BrowseResult]


class FeatureInitState(StrEnum):
    OPEN = "open"  # feature has not been initalized yet
    PENDING = "pending"  # feature init has been started
    DONE = "done"  # feature is ready to be used for the entity
    ERROR = "error"  # something went wrong while initializing.


@dataclass
class FeatureSubscribeDataRequest:
    node_id: ua.NodeId
    feature: "FeatureNode"
    attr: AttributeIds

    handler: Callable[[Node, DataChangeEvent], None]


@dataclass
class FeatureSubscribeEventRequest:
    node_id: ua.NodeId
    feature: "FeatureNode"
    handler: Callable[[Event], None]


@dataclass
class FeatureSubscribeRequest:
    subscriptions: list[FeatureSubscribeDataRequest | FeatureSubscribeEventRequest]


@dataclass
class FeatureValueReadRequest:
    read_requests: list[ua.ReadValueId]
    feature: "FeatureNode"


@dataclass
class FeatureValueReadResult:
    read_results: list[ua.DataValue]


class EntityNodeData(JsonOutModel):
    """Base Model used for FeatureNode and ComponentNode"""

    opc_node: OPCNodeData
    """Basic node data"""

    entity: Any | None
    """The entity itself, containing the data used for frontend components"""
    entity_id: uuid.UUID
    """Unique ID to identify a single entity. Not re-useable between reconnects."""
    entity_type: str | None
    """String describing the entity_type. The frontend will choose the rendering component based on this."""

    init_state: FeatureInitState
    """Shows the init state. Should be 'done'."""
    init_error: str | None
    """Contains eventual error messages that happened during initialization"""

    parent_component_node_entity_id: uuid.UUID | None
    """EntityId of the parent component. Is None, if no parent component is present."""

    features: list["FeatureNodeData"]
    """List of features contained in this feature or component."""


class FeatureNodeData(EntityNodeData):
    """Data representation of a FeatureNode"""

    parent_feature_node_entity_id: uuid.UUID | None
    """EntityId of the parent feature. Is None, if no parent feature is present."""


class ComponentNodeData(EntityNodeData):
    """Data representation of a ComponentNode."""

    children: list["ComponentNodeData"]
    """List of child components"""


class FeatureNode:
    opc_node: OPCNode
    opc_namespace: OPCNamespace

    parent_component_node: "ComponentNode"
    parent_feature_node: Union["FeatureNode", None]

    entity: FeatureNodeEntity | None
    entity_id: uuid.UUID
    entity_type: str | None

    init_state: FeatureInitState
    init_error: str | None

    event_bus: EventBus | None

    features: list["FeatureNode"]

    def __init__(
        self,
        opc_node: OPCNode,
        opc_namespace: OPCNamespace,
        parent_component_node: "ComponentNode",
        parent_feature_node: Union["FeatureNode", None] = None,
    ):
        self.opc_node = opc_node
        self.opc_namespace = opc_namespace

        self.entity = None
        self.entity_id = uuid.uuid4()
        self.entity_type = None

        self.parent_component_node = parent_component_node
        self.parent_feature_node = parent_feature_node

        self.init_state = FeatureInitState.OPEN
        self.init_error = None

        self.event_bus = None

        self.features = []

    ## STEP POPULATION
    @abstractmethod
    def _populate_step(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        """_populate_step() is the internal method any feature needs to implement to populate itself.
        It is usually called via next_populate_step()
        """
        return None

    def next_populate_step(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        """next_populate_step() will continue the population process of a feature by providing the last result (initially it is None).
        This will catch all exceptions and return an init_state of ERROR if anything raises."""
        try:
            return self._populate_step(last_result=last_result)
        except Exception as e:  # noqa: BLE001 # catch all to prevent silent fails on features
            self.init_state = FeatureInitState.ERROR
            self.init_error = str(e)
            return None

    ## SUBSCRIPTION REQUEST
    @abstractmethod
    def _request_subscription(self) -> FeatureSubscribeRequest | None:
        """_request_subscription() is the internal method that any feature which needs subscriptions needs to implement.
        The EventBus is available via self.event_bus."""
        return None

    def request_subscription(
        self, event_bus: EventBus
    ) -> FeatureSubscribeRequest | None:
        """request_subscription() is called to gather all subscription requests.
        This will call the internal _request_subscription() method of the actual feature.
        Returning None means no subscriptions are requested.
        The event bus is automatically added to the feature in this.
        All exceptions are catched and result in ERROR state for the feature."""
        try:
            self.event_bus = event_bus
            return self._request_subscription()
        except Exception as e:  # noqa: BLE001 # catch all to prevent silent fails on features
            self.init_state = FeatureInitState.ERROR
            self.init_error = str(e)
            return None

    def handle_subscription_failure(self, status: ua.StatusCode) -> None:
        """This method will be called when the creation of the subscription failed"""
        self.init_state = FeatureInitState.ERROR
        self.init_error = (
            f"Failed to initialize subscriptions. StatusCode: {status.name}"
        )

    ## VALUE READ
    @abstractmethod
    def _request_value(self) -> FeatureValueReadRequest | None:
        """_request_value() is the internal method a feature needs to implement if it wants to do a final read."""
        return None

    def request_value(self) -> FeatureValueReadRequest | None:
        """request_value() is called to gather all final read requests to read value (or other attributes)
        after subscriptions have been established. All exceptions are catched and result in ERROR state for the feature."""
        try:
            return self._request_value()
        except Exception as e:  # noqa: BLE001 # catch all to prevent silent fails on features
            self.init_state = FeatureInitState.ERROR
            self.init_error = str(e)
            return None

    @abstractmethod
    def _handle_value_result(self, result: FeatureValueReadResult) -> None:
        """handle_value_result() is called to return the values requested by request_value()"""
        return

    def handle_value_result(self, result: FeatureValueReadResult) -> None:
        """handle_value_result() is called with the results of the request_value().
        All exceptions are catched and result in ERROR state for the feature."""
        try:
            return self._handle_value_result(result)
        except Exception as e:  # noqa: BLE001 # catch all to prevent silent fails on features
            self.init_state = FeatureInitState.ERROR
            self.init_error = str(e)
            return None

    ## ACTION
    @abstractmethod
    async def handle_action(self, action: GenericAction) -> None:
        """handle_action() is called whenever any action has been received for the entityId of this feature.
        This method does not catch exceptions, as this method is expected to raise up to FastAPI."""
        raise NotImplementedError("This feature does not support actions")

    ## DATA
    def get_data(self) -> FeatureNodeData:
        return FeatureNodeData(
            # basic node data
            opc_node=self.opc_node.get_data(),
            # entity data
            entity=self.entity.get_data() if self.entity is not None else None,
            entity_id=self.entity_id,
            entity_type=self.entity_type if self.entity_type is not None else None,
            # state information
            init_state=self.init_state,
            init_error=self.init_error,
            # parent entities if exist
            parent_component_node_entity_id=self.parent_component_node.entity_id
            if self.parent_component_node is not None
            else None,
            parent_feature_node_entity_id=self.parent_feature_node.entity_id
            if self.parent_feature_node is not None
            else None,
            # child features
            features=[feat.get_data() for feat in self.features],
        )


class ComponentNode:
    opc_node: OPCNode
    opc_namespace: OPCNamespace

    entity: ComponentEntity | None
    entity_id: uuid.UUID
    entity_type: str | None

    parent_component_node: Union["ComponentNode", None]

    init_state: FeatureInitState
    init_error: str | None

    features: list[FeatureNode]

    children: list["ComponentNode"]

    def __init__(
        self,
        opc_node: OPCNode,
        opc_namespace: OPCNamespace,
        parent_component_node: Union["ComponentNode", None] = None,
    ):
        self.opc_node = opc_node
        self.opc_namespace = opc_namespace
        self.entity = None
        self.entity_id = uuid.uuid4()
        self.entity_type = "Component"

        self.parent_component_node = parent_component_node

        self.init_state = FeatureInitState.OPEN
        self.init_error = None

        self.features = []
        self.children = []

    def get_data(self) -> ComponentNodeData:
        return ComponentNodeData(
            # basic node data
            opc_node=self.opc_node.get_data(),
            # entity data
            entity=self.entity.get_data() if self.entity is not None else None,
            entity_id=self.entity_id,
            entity_type=self.entity_type if self.entity_type is not None else None,
            # state information
            init_state=self.init_state,
            init_error=self.init_error,
            # parent component
            parent_component_node_entity_id=self.parent_component_node.entity_id
            if self.parent_component_node is not None
            else None,
            # features
            features=[feat.get_data() for feat in self.features],
            # child components
            children=[child.get_data() for child in self.children],
        )


def print_component_trees(trees: list[ComponentNode]) -> None:
    """Print component trees in a human-readable tree format."""

    def print_tree(tree: ComponentNode, prefix: str = "", is_last: bool = True) -> None:
        name = tree.opc_node.browse_name.Name
        ns_idx = tree.opc_node.browse_name.NamespaceIndex
        child_count = len(tree.opc_node.get_children())

        branch = "└── " if is_last else "├── "
        print(f"{prefix}{branch}{ns_idx}:{name}[{child_count}]")

        for child_node in tree.opc_node.get_children():
            print(
                f"{prefix}    +{child_node.browse_name.NamespaceIndex}:{child_node.browse_name.Name}[{len(child_node.children)}]"
            )

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
