## Generic Stuff
from enum import Enum
from typing import Any
import uuid

from pydantic import BaseModel, computed_field, AliasGenerator, ConfigDict
from pydantic.alias_generators import to_camel


# base class for all json based models. converts snake_case_style to camelCaseStyle for JSON in both directions
class JsonBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        )
    )


class JsonOutModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        )
    )


class GenericUpdateEntityType(str, Enum):
    Machine = "Machine"
    Server = "Server"
    Component = "Component"
    Skill = "Skill"
    Method = "Method"
    Variable = "Variable"
    PinGuard = "PinGuard"


class GenericUpdateMessage[T](JsonOutModel):
    entity_id: uuid.UUID
    entity_type: GenericUpdateEntityType
    update_content: T

    @computed_field
    @property
    def update_type(self) -> str:
        return self.update_content.__class__.__name__


class HealthResponse(JsonOutModel):
    is_healthy: bool


## Actions
class GenericActionType(str, Enum):
    WriteParameter = "WriteParameter"
    WriteParameterList = "WriteParameteList"
    MethodCall = "MethodCall"
    SkillStart = "SkillStart"
    SkillReset = "SkillReset"
    SkillHalt = "SkillHalt"
    SkillSuspend = "SkillSuspend"


class GenericActionTargetEntityType(str, Enum):
    Skill = "Skill"
    Component = "Component"
    Method = "Method"
    Machine = "Machine"


class GenericActionRequest(JsonBaseModel):
    entity_id: uuid.UUID
    entity_type: GenericActionTargetEntityType
    action_type: GenericActionType
    action_content: Any
