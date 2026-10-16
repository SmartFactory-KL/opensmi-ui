from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.opc_node import OPCNode


class NotificationEntityData(FeatureNodeEntityData):
    name: str


class NotificationEntity(FeatureNodeEntity):
    name: str

    def __init__(self, opc_node: OPCNode):
        self.name = opc_node.browse_name.Name

    def get_data(self) -> NotificationEntityData:
        return NotificationEntityData(name=self.name)
