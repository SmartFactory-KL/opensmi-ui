from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureNode,
)
from opensmi_ui.opc_model.opc_node import OPCNode

logger = get_module_logger("opc_model.features.notification")


class NotificationFeatureNode(FeatureNode):
    def __init__(self, opc_node: OPCNode, parent_component_node: ComponentNode):
        super().__init__(opc_node=opc_node, parent_component_node=parent_component_node)
        # TODO

    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        # check if a "Messages" node exists

        return None
