from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.opc_node import OPCNode


class MachineryItemStateEntityData(FeatureNodeEntityData):
    name: str
    current_state: str


class MachineryItemStateEntity(FeatureNodeEntity):
    name: str
    current_state: str

    def __init__(self, opc_node: OPCNode):
        self.name = opc_node.browse_name.Name
        self.current_state = "unknown"

        for child in opc_node.children:
            if child.browse_name.Name == "CurrentState":
                self.current_state = str(child.attributes.get("Value", "unknown"))

    def get_data(self) -> MachineryItemStateEntityData:
        return MachineryItemStateEntityData(
            name=self.name, current_state=self.current_state
        )
