from typing import Any
from uuid import UUID

from opensmi_ui.model.json import JsonInModel


class GenericAction(JsonInModel):
    entity_id: UUID
    action: dict[str, Any]
    action_type: str
