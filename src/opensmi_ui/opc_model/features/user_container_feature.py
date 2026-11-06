from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.user_container_entity import UserContainerEntity
from opensmi_ui.opc_model.feature_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
)
from opensmi_ui.opc_model.features.user_feature import UserFeatureNode
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_session.namespace import OPCNamespace

logger = get_module_logger("opc_model.features.user_container")


class UserContainerFeatureNode(FeatureNode):
    def __init__(
        self,
        opc_node: OPCNode,
        opc_namespace: OPCNamespace,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(
            opc_node=opc_node,
            opc_namespace=opc_namespace,
            parent_component_node=parent_component_node,
            parent_feature_node=parent_feature_node,
        )
        self.entity_type = "UserContainer"

        # create child resources (recursive or not?)
        for child in opc_node.children:
            ref = child.reference_type

            if not ref or ref.Identifier != ua.object_ids.ObjectIds.HasComponent:
                continue

            user_feature = UserFeatureNode(
                opc_node=child,
                opc_namespace=opc_namespace,
                parent_component_node=parent_component_node,
                parent_feature_node=self,
            )

            self.features.append(user_feature)

    def _populate_step(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        self.entity = UserContainerEntity(opc_node=self.opc_node)
        self.init_state = FeatureInitState.DONE
        return None
