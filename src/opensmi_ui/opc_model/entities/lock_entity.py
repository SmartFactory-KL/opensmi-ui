from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.opc_node import OPCNode


class LockEntityData(FeatureNodeEntityData):
    name: str

    is_locked: bool
    locking_user: str
    locking_client: str


class LockEntity(FeatureNodeEntity):
    content: LockEntityData

    def __init__(self, opc_node: OPCNode):
        self.content = LockEntityData(
            name=opc_node.browse_name.Name,
            is_locked=False,
            locking_user="",
            locking_client="",
        )

    def get_data(self) -> LockEntityData:
        return self.content
