from asyncua import ua

from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.features.variable_modifier.modifier import (
    VariableModifier,
    VariableModifierData,
)


class RangeModifierContent(JsonOutModel):
    low: float
    high: float


class RangeModifier(VariableModifier):
    content: RangeModifierContent

    def __init__(self, input: ua.Variant):
        if not isinstance(input, ua.Variant):
            raise TypeError(
                f"Range Modifier can only be created from Variant, but input was {type(input)} instead"
            )

        if not isinstance(input.Value, ua.Range):
            raise TypeError(
                f"Range Modifier can only be created from Variant[Range], got Variant[{type(input.Value)}] instead"
            )

        self.content = RangeModifierContent(low=input.Value.Low, high=input.Value.High)

    def get_data(self) -> VariableModifierData:
        return VariableModifierData(
            modifier_type="RangeModifier", modifier_content=self.content
        )
