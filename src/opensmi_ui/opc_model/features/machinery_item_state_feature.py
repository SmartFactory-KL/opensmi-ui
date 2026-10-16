from enum import StrEnum

from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.machinery_item_state_entity import (
    MachineryItemStateEntity,
)
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureNode,
)
from opensmi_ui.opc_model.opc_node import OPCNode

logger = get_module_logger("opc_model.features.resource")


class MachineryItemStateInitState(StrEnum):
    OPEN = "open"
    VALUE_READ = "value_read"
    DONE = "done"
    ERROR = "error"


class MachineryItemStateFeatureNode(FeatureNode):
    _init_state: MachineryItemStateInitState

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self._init_state = MachineryItemStateInitState.OPEN
        self.entity_type = "MachineryItemState"

    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        match self._init_state:
            case MachineryItemStateInitState.OPEN:
                req = FeatureInitRequest(
                    browse_requests=[], read_requests=[], feature=self
                )

                for child in self.opc_node.children:
                    req.read_requests.append(
                        ua.ReadValueId(
                            NodeId=child.node_id,
                            AttributeId=ua.attribute_ids.AttributeIds.Value,
                        )
                    )

                self._init_state = MachineryItemStateInitState.VALUE_READ
                return req
            case MachineryItemStateInitState.VALUE_READ:
                if last_result is None:
                    self._init_state = MachineryItemStateInitState.ERROR
                    return None

                for idx, child in enumerate(self.opc_node.children):
                    val_result = last_result.read_results[idx]

                    if val_result.StatusCode is None or val_result.StatusCode.is_bad():
                        continue

                    if val_result.Value is not None:
                        child.attributes["Value"] = val_result.Value.Value

                self.entity = MachineryItemStateEntity(opc_node=self.opc_node)
                self._init_state = MachineryItemStateInitState.DONE
            case _:
                return None

        return None
