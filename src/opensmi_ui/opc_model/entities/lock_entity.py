from uuid import UUID

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.opc_node import OPCNode

logger = get_module_logger("opc_model.entities.lock")


class LockIsLockedUpdate(JsonOutModel):
    entity_id: UUID
    timestamp: str
    new_is_locked: bool


class LockLockingUserUpdate(JsonOutModel):
    entity_id: UUID
    timestamp: str
    new_user: str


class LockLockingClientUpdate(JsonOutModel):
    entity_id: UUID
    timestamp: str
    new_client: str


class LockEntityData(FeatureNodeEntityData):
    name: str

    is_locked: bool
    is_locked_last_change: str

    locking_user: str
    locking_user_last_change: str

    locking_client: str
    locking_client_last_change: str


class LockEntity(FeatureNodeEntity):
    content: LockEntityData

    def __init__(self, opc_node: OPCNode):
        try:
            is_locked_node = opc_node.get_first_child_node_for_name("Locked")
            locking_user_node = opc_node.get_first_child_node_for_name("LockingUser")
            locking_client_node = opc_node.get_first_child_node_for_name(
                "LockingClient"
            )

            self.content = LockEntityData(
                name=opc_node.browse_name.Name,
                is_locked=is_locked_node.attributes.get("Value", False).Value,
                is_locked_last_change=str(
                    is_locked_node.attributes.get("LastChange", "")
                ),
                locking_user=locking_user_node.attributes.get("Value", "").Value,
                locking_user_last_change=str(
                    locking_user_node.attributes.get("LastChange", "")
                ),
                locking_client=locking_client_node.attributes.get("Value", "").Value,
                locking_client_last_change=str(
                    locking_client_node.attributes.get("LastChange", "")
                ),
            )
        except:  # noqa: E722 # unknown exceptions at this point
            logger.exception("Failed to create LockEntity")

    def get_data(self) -> LockEntityData:
        return self.content

    def apply_update(
        self,
        update: JsonOutModel,
    ):
        if isinstance(update, LockIsLockedUpdate):
            self.content.is_locked = update.new_is_locked
            self.content.is_locked_last_change = str(update.timestamp)
        elif isinstance(update, LockLockingUserUpdate):
            self.content.locking_user = update.new_user
            self.content.locking_user_last_change = str(update.timestamp)
        elif isinstance(update, LockLockingClientUpdate):
            self.content.locking_client = update.new_client
            self.content.locking_client_last_change = str(update.timestamp)
        else:
            return
