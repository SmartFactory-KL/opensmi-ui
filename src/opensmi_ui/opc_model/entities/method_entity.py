from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.opc_node import OPCNode


class MethodEntityData(FeatureNodeEntityData):
    name: str
    min_access_level: int


class MethodEntity(FeatureNodeEntity):
    content: MethodEntityData

    def __init__(self, opc_node: OPCNode):
        self.content = MethodEntityData(
            name=opc_node.browse_name.Name, min_access_level=0
        )

        for child in opc_node.children:
            if child.browse_name.Name == "MinAccessLevel":
                val = child.attributes["Value"]

                self.content.min_access_level = int(val.Value)

    def get_data(self) -> MethodEntityData:
        return self.content
