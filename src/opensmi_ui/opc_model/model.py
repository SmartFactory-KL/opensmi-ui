from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.node import OPCNode
from opensmi_ui.opc_session.session import OPCSession

logger = get_module_logger("opc_model")


class MIFeature(Protocol):
    opc_node: OPCNode

    # lifecycle
    async def add_subscriptions(self) -> None: ...
    async def read_values(self, opc_session: OPCSession) -> None: ...

    def get_dto(self) -> Mapping[str, object]: ...


# MIF = MachineryItemFeature
class MIFContainer:
    features: list[MIFeature]

    def __init__(self, opc_node: OPCNode):
        self.opc_node = opc_node
        self.features = []

    def add_feature(self, feature):
        self.features.append(feature)


@dataclass
class ComponentTree:
    node: OPCNode
    children: list["ComponentTree"]

    mifco: MIFContainer | None = None


@dataclass(frozen=True)
class ComponentTreeReadItem:
    node: OPCNode
    parent_tree: ComponentTree | None


@dataclass(frozen=True)
class NodeReadItem:
    node_id: ua.NodeId
    parent_node: OPCNode | None
