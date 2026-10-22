from datetime import datetime
from uuid import UUID

from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_model.value_read import variant_value_to_string


class SkillStateStateUpdate(JsonOutModel):
    entity_id: UUID
    new_state: str | int
    timestamp: datetime | None


class SkillStateEntityData(FeatureNodeEntityData):
    name: str
    current_state: int | str
    current_state_last_change: datetime | None


class SkillStateEntity(FeatureNodeEntity):
    content: SkillStateEntityData

    def __init__(self, opc_node: OPCNode):
        current_state = opc_node.attributes.get("Value", 11)

        self.content = SkillStateEntityData(
            name=opc_node.browse_name.Name,
            current_state=variant_value_to_string(current_state),
            current_state_last_change=None,
        )

    def get_data(self) -> SkillStateEntityData:
        return self.content

    def apply_update(self, update: JsonOutModel):
        if isinstance(update, SkillStateStateUpdate):
            self.content.current_state = update.new_state
            self.content.current_state_last_change = update.timestamp
        else:
            return
