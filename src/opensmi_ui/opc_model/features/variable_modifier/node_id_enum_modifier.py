from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.features.variable_modifier.modifier import (
    VariableModifier,
    VariableModifierData,
)
from opensmi_ui.opc_model.opc_types import NodeIdData

logger = get_module_logger("opc_model.features.variable_modifier.enum")


class NodeIdEnumModifierContent(JsonOutModel):
    valid_values: dict[str, NodeIdData]


class NodeIdEnumModifier(VariableModifier):
    content: NodeIdEnumModifierContent

    def __init__(self, references: list[ua.ReferenceDescription]):
        valid_values: dict[str, NodeIdData] = {}

        for ref in references:
            valid_values[ref.BrowseName.Name] = NodeIdData.from_ua(ref.NodeId)

        self.content = NodeIdEnumModifierContent(valid_values=valid_values)

    def get_data(self) -> VariableModifierData:
        return VariableModifierData(
            modifier_type="NodeIdEnumModifier", modifier_content=self.content
        )
