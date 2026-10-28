from asyncua import ua

from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.features.variable_modifier.modifier import (
    VariableModifier,
    VariableModifierData,
)
from opensmi_ui.opc_model.opc_node import LocalizedTextData


class UnitModifierContent(JsonOutModel):
    display_name: LocalizedTextData
    description: LocalizedTextData
    unit_id: int


class UnitModifier(VariableModifier):
    content: UnitModifierContent

    def __init__(self, input: ua.Variant):
        if not isinstance(input, ua.Variant):
            raise TypeError(
                f"Unit Modifier can only be created from Variant, but input was {type(input)} instead"
            )

        if not isinstance(input.Value, ua.EUInformation):
            raise TypeError(
                f"Unit Modifier can only be created from Variant[EUInformation], got Variant[{type(input.Value)}] instead"
            )

        self.content = UnitModifierContent(
            description=LocalizedTextData.from_ua(input.Value.Description),
            display_name=LocalizedTextData.from_ua(input.Value.DisplayName),
            unit_id=input.Value.UnitId,
        )

    def get_data(self) -> VariableModifierData:
        return VariableModifierData(
            modifier_type="UnitModifier", modifier_content=self.content
        )
