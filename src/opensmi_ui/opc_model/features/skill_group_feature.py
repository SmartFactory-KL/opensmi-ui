from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.skill_group_entity import SkillGroupEntity
from opensmi_ui.opc_model.feature_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
)
from opensmi_ui.opc_model.features.skill_feature import SkillFeatureNode
from opensmi_ui.opc_model.opc_node import OPCNode

logger = get_module_logger("opc_model.features.skill_group")


class SkillGroupFeatureNode(FeatureNode):
    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self.entity_type = "SkillGroup"  # SkillGroup = Execution + Feasibility + Precondition, all optional

        # create child resources (recursive or not?)
        for child in opc_node.children:
            ref = child.reference_type

            if not ref or ref.Identifier != ua.object_ids.ObjectIds.HasComponent:
                continue

            match child.browse_name.Name:
                case "SkillExecution" | "FeasibilityCheck" | "PreconditionCheck":
                    self.features.append(
                        SkillFeatureNode(
                            opc_node=child,
                            parent_component_node=parent_component_node,
                            parent_feature_node=self,
                        )
                    )

    def _populate_step(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        self.entity = SkillGroupEntity(opc_node=self.opc_node)
        self.init_state = FeatureInitState.DONE
        return None
