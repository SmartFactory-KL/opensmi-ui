from abc import abstractmethod
from typing import Any

from opensmi_ui.model.json import JsonOutModel


class VariableModifierData(JsonOutModel):
    modifier_type: str
    modifier_content: Any


class VariableModifier:
    @abstractmethod
    def get_data(self) -> VariableModifierData: ...
