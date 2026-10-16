from enum import StrEnum

from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.lock_entity import LockEntity
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureNode,
)
from opensmi_ui.opc_model.opc_node import OPCNode

logger = get_module_logger("opc_model.features.lock")


class LockInitState(StrEnum):
    OPEN = "open"
    RECEIVE_LOCKING_NODES = "receive_locking_nodes"
    DONE = "done"


class LockFeatureNode(FeatureNode):
    init_state: LockInitState

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self._init_state = LockInitState.OPEN
        self.entity_type = "Lock"

    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        match self._init_state:
            case LockInitState.OPEN:
                req = FeatureInitRequest(
                    browse_requests=[], read_requests=[], feature=self
                )

                # read values for data nodes
                for child_node in self.opc_node.children:
                    match child_node.browse_name.Name:
                        case (
                            "Locked"
                            | "LockingUser"
                            | "LockingClient"
                            | "RemainingLockTime"
                        ):
                            req.read_requests.append(
                                ua.ReadValueId(
                                    NodeId=child_node.node_id,
                                    AttributeId=ua.attribute_ids.AttributeIds.Value,
                                )
                            )
                        case _:
                            logger.info(
                                f"skipped lock node: {child_node.browse_name.Name}"
                            )
                            continue

                self._init_state = LockInitState.RECEIVE_LOCKING_NODES
                return req
            case LockInitState.RECEIVE_LOCKING_NODES:
                # logger.info(last_result)

                self.entity = LockEntity(opc_node=self.opc_node)
                return None
            case _:
                return None
