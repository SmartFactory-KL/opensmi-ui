from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.opc_node import OPCNode


class SkillStateEntityData(FeatureNodeEntityData):
    name: str
    current_state: int | str


class SkillStateEntity(FeatureNodeEntity):
    content: SkillStateEntityData

    def __init__(self, opc_node: OPCNode):
        current_state = opc_node.attributes.get("Value", 11)

        self.content = SkillStateEntityData(
            name=opc_node.browse_name.Name, current_state=current_state
        )

    def get_data(self) -> SkillStateEntityData:
        return self.content
