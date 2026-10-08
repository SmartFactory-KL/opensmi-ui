import pathlib
import uuid
from enum import Enum
from typing import Any

from pydantic import AliasGenerator, BaseModel, ConfigDict, computed_field
from pydantic.alias_generators import to_camel


# basic error class for non-enabled stuff
class ModuleDisabledError(RuntimeError):
    """Raised whenever a module is simply not enabled but functionality was still used"""


# base class for all json based models. converts snake_case_style to camelCaseStyle for JSON in both directions
class JsonBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        json_encoders={pathlib.PurePosixPath: str},
        populate_by_name=True,
    )


class JsonOutModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
        json_encoders={pathlib.PurePosixPath: str},
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
    entity_id: uuid.UUID | None
    entity_type: GenericUpdateEntityType
    update_content: T

    @computed_field
    @property
    def update_type(self) -> str:
        return self.update_content.__class__.__name__


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
