import datetime
from enum import Enum
from model.common_types import (
    GenericActionRequest,
    GenericActionType,
    GenericUpdateEntityType,
    GenericUpdateMessage,
    JsonBaseModel,
    JsonOutModel,
)
from model.node_types import SimpleDataValueDto


# Genericals
class LockingState(JsonOutModel):
    locked: bool
    locking_user: str
    locking_client: str
    locked_since: datetime.datetime | None


class VariableTargetType(str, Enum):
    Monitoring = "Monitoring"
    FinalResultData = "FinalResultData"
    Parameter = "Parameter"
    Attribute = "Attribute"


# Requests
class WriteParameterContent(JsonBaseModel):
    parameter_node_id: str
    parameter_name: str
    parameter_new_value: str | int | float


class WriteParameterRequest(GenericActionRequest):
    action_type: GenericActionType = GenericActionType.WriteParameter
    action_content: WriteParameterContent


# Responses


# Update Wrappers
class MachineUpdateMessage[T](GenericUpdateMessage[T]):
    entity_type: GenericUpdateEntityType = GenericUpdateEntityType.Machine


class ComponentUpdateMessage[T](GenericUpdateMessage[T]):
    entity_type: GenericUpdateEntityType = GenericUpdateEntityType.Component


class SkillUpdateMessage[T](GenericUpdateMessage[T]):
    entity_type: GenericUpdateEntityType = GenericUpdateEntityType.Skill


class VariableUpdateMessage[T](GenericUpdateMessage[T]):
    entity_type: GenericUpdateEntityType = GenericUpdateEntityType.Variable


# Updates
class ComponentStateUpdate(JsonOutModel):
    new_state: str | int


class ComponentNewMessageUpdate(JsonOutModel):
    severity: int
    code: str
    text: str


class MachineLockStateUpdate(JsonOutModel):
    is_locked: bool


class MachineLockUserUpdate(JsonOutModel):
    new_locking_user: str


class SkillStateUpdate(JsonOutModel):
    new_state: str


class VariableDataValueUpdate(SimpleDataValueDto):
    pass
