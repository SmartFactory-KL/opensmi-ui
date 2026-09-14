from opensmi_ui.model.common_types import (
    GenericUpdateEntityType,
    GenericUpdateMessage,
    JsonBaseModel,
    JsonOutModel,
)


class PinGuardState(JsonOutModel):
    is_locked: bool
    is_enabled: bool


class PinGuardUnlockRequest(JsonBaseModel):
    pin: str


class PinGuardUpdateMessage[T](GenericUpdateMessage[T]):
    entity_type: GenericUpdateEntityType = GenericUpdateEntityType.PinGuard


class PinGuardStateUpdate(JsonOutModel):
    new_is_locked: bool
