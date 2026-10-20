from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.opc_node import OPCNode


class UserEntityData(FeatureNodeEntityData):
    name: str

    allow_multiple: str
    current_access_level: str
    max_access_level: str
    is_present: str


class UserEntity(FeatureNodeEntity):
    content: UserEntityData

    def __init__(self, opc_node: OPCNode):
        # read child values

        vals = {}
        for child in opc_node.children:
            match child.browse_name.Name:
                case "AllowMultiple" | "UserLevel" | "MaxAccessLevel" | "IsPresent":
                    if "Value" in child.attributes:
                        vals[child.browse_name.Name] = str(
                            child.attributes["Value"].Value
                            if child.attributes["Value"] is not None
                            else None
                        )

        self.content = UserEntityData(
            name=opc_node.browse_name.Name,
            allow_multiple=vals.get("AllowMultiple", False),
            current_access_level=vals.get("UserLevel", 0),
            is_present=vals.get("IsPresent", False),
            max_access_level=vals.get("MaxAccessLevel", 0),
        )

    def get_data(self) -> UserEntityData:
        return self.content
