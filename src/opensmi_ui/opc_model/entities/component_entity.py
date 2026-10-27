from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.opc_node import OPCNode


class ComponentEntityData(FeatureNodeEntityData):
    name: str
    component_type: str


class ComponentEntity(FeatureNodeEntity):
    name: str
    component_type: str

    def __init__(self, opc_node: OPCNode):
        self.name = opc_node.browse_name.Name
        self.component_type = "GenericComponent"

        if opc_node.opc_type is not None:
            self.component_type = opc_node.opc_type.Name

    def get_data(self) -> ComponentEntityData:
        return ComponentEntityData(name=self.name, component_type=self.component_type)
