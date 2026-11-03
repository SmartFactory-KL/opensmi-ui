from uuid import UUID

from asyncua.ua import Variant

from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.opc_node import OPCNode


class UserIsPresentUpdate(JsonOutModel):
    entity_id: UUID
    timestamp: str
    new_is_present: bool


class UserEntityData(FeatureNodeEntityData):
    name: str

    allow_multiple: bool
    current_access_level: int
    max_access_level: int
    is_present: bool


class UserEntity(FeatureNodeEntity):
    content: UserEntityData

    def __init__(self, opc_node: OPCNode):
        # read child values

        vals = {}
        for child in opc_node.children:
            match child.browse_name.Name:
                case "AllowMultiple" | "IsPresent":
                    val = child.attributes.get("Value", None)
                    if val is None:
                        continue

                    if isinstance(val, Variant):
                        val = val.Value

                    vals[child.browse_name.Name] = bool(val)
                case "UserLevel" | "MaxAccessLevel":
                    val = child.attributes.get("Value", None)
                    if val is None:
                        continue

                    if isinstance(val, Variant):
                        val = val.Value

                    vals[child.browse_name.Name] = int(val)

        self.content = UserEntityData(
            name=opc_node.browse_name.Name,
            allow_multiple=vals.get("AllowMultiple", False),
            is_present=vals.get("IsPresent", False),
            current_access_level=vals.get("UserLevel", 0),
            max_access_level=vals.get("MaxAccessLevel", 0),
        )

    def get_data(self) -> UserEntityData:
        return self.content
