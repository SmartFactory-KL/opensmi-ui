from asyncua.ua import LocalizedText

from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.features.variable_modifier.range_modifier import JsonOutModel
from opensmi_ui.opc_model.features.variable_modifier.unit_modifier import (
    LocalizedTextData,
)
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_model.value_read import UUID


class MachineryItemStateStateUpdate(JsonOutModel):
    entity_id: UUID
    new_state: LocalizedTextData


class MachineryItemStateEntityData(FeatureNodeEntityData):
    name: str
    current_state: LocalizedTextData | None


class MachineryItemStateEntity(FeatureNodeEntity):
    name: str
    current_state: LocalizedTextData | None

    def __init__(self, opc_node: OPCNode):
        self.name = opc_node.browse_name.Name
        self.current_state = None

        for child in opc_node.children:
            if child.browse_name.Name == "CurrentState":
                state_val = child.attributes.get("Value", None)

                if isinstance(state_val, LocalizedText):
                    self.current_state = LocalizedTextData.from_ua(state_val)

    def get_data(self) -> MachineryItemStateEntityData:
        return MachineryItemStateEntityData(
            name=self.name, current_state=self.current_state
        )

    def apply_update(self, update: JsonOutModel):
        if isinstance(update, MachineryItemStateStateUpdate):
            self.current_state = update.new_state
