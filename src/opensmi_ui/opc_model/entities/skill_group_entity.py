from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.opc_node import OPCNode


class SkillGroupEntityData(FeatureNodeEntityData):
    name: str
    is_continuous: bool


class SkillGroupEntity(FeatureNodeEntity):
    name: str
    is_continuous: bool

    def __init__(self, opc_node: OPCNode):
        self.name = opc_node.browse_name.Name
        self.is_continuous = opc_node.opc_type.Name.lower().startswith("continuous")

    def get_data(self) -> SkillGroupEntityData:
        return SkillGroupEntityData(name=self.name, is_continuous=self.is_continuous)
