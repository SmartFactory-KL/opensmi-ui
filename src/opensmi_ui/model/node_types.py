# Enums
import uuid
from enum import Enum
from typing import Any

from asyncua.ua import VariantType
from pydantic import ConfigDict

from opensmi_ui.model.common import JsonOutModel


class RemoteVariableValueType(str, Enum):
    Enum = "Enum"  # There is a set of valid values in type_annotation
    FloatRange = "FloatRange"  # There is a range with min and max in type_annotation
    Boolean = "Boolean"  # Only used to display a checkbox, no annotations
    ImageJPG = "ImageJPG"  # JPG Image
    ImagePNG = "ImagePNG"  # PNG Image
    ImageBMP = "ImageBMP"  # BMP Image
    ImageGIF = "ImageGIF"  # GIF Image
    Text = "Text"  # Sums up all other types - means: "nothing special, just text"


class VariantValueDto(JsonOutModel):
    variant_type: VariantType
    value: Any
    dimensions: list[int] | None


class SimpleDataValueDto(JsonOutModel):
    value: VariantValueDto
    status_code: int
    timestamp: float


# Models for nodes
class RemoteVariableDto(JsonOutModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = ""
    entity_id: uuid.UUID
    node_id: str = ""
    data_content: SimpleDataValueDto
    remote_variable_type: RemoteVariableValueType = RemoteVariableValueType.Text
    remote_variable_annotation: Any
    timestamp: str | None = None
    is_writable: bool = False
    unit: str | None = None
    children: list["RemoteVariableDto"]
    parent_entity_id: uuid.UUID | None


class MethodDto(JsonOutModel):
    name: str = ""
    node_id: str = ""
    entity_id: uuid.UUID
    type: str = ""
    parameter_set: list[RemoteVariableDto]
    monitoring: list[RemoteVariableDto]
    final_result_data: list[RemoteVariableDto]
    parent_entity_id: uuid.UUID | None
    parent_node_id_list: list[str]
    min_access_level: int | None = None


class SkillDto(JsonOutModel):
    name: str = ""
    node_id: str = ""
    entity_id: uuid.UUID
    type: str = ""
    current_state: str | None = None
    parameter_set: list[RemoteVariableDto]
    monitoring: list[RemoteVariableDto]
    final_result_data: list[RemoteVariableDto]
    depends_on: list[str]
    dependency_of: list[str]
    parent_entity_id: uuid.UUID | None
    parent_node_id_list: list[str]
    is_suspendable: bool = False
    min_access_level: int | None = None


class ComponentDto(JsonOutModel):
    name: str = ""
    node_id: str = ""
    entity_id: uuid.UUID
    type: str = ""
    current_state: str | None = None
    skill_set: list[SkillDto]
    methods: list[MethodDto]
    monitoring: list[RemoteVariableDto]
    attributes: list[RemoteVariableDto]
    parameter_set: list[RemoteVariableDto]
    components: list["ComponentDto"]
    parent_entity_id: uuid.UUID | None
    parent_node_id_list: list[str]


class LockingModuleDto(JsonOutModel):
    is_enabled: bool
    is_simulated: bool
    is_locked: bool
    is_locked_since: str
    locking_user: str
    locking_client: str


class MachineDto(ComponentDto):
    locking_module: LockingModuleDto
