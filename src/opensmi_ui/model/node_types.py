# Enums
import uuid
from enum import Enum
from typing import Any, List, Optional

from asyncua.ua import VariantType
from pydantic import ConfigDict

from model.common_types import JsonOutModel


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
    dimensions: Optional[List[int]]


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
    children: List["RemoteVariableDto"] = []
    parent_entity_id: uuid.UUID | None


class MethodDto(JsonOutModel):
    name: str = ""
    node_id: str = ""
    entity_id: uuid.UUID
    type: str = ""
    parameter_set: List[RemoteVariableDto] = []
    monitoring: List[RemoteVariableDto] = []
    final_result_data: List[RemoteVariableDto] = []
    parent_entity_id: uuid.UUID | None
    parent_node_id_list: List[str]
    min_access_level: int | None = None


class SkillDto(JsonOutModel):
    name: str = ""
    node_id: str = ""
    entity_id: uuid.UUID
    type: str = ""
    current_state: str | None = None
    parameter_set: List[RemoteVariableDto] = []
    monitoring: List[RemoteVariableDto] = []
    final_result_data: List[RemoteVariableDto] = []
    depends_on: List[str] = []
    dependency_of: List[str] = []
    parent_entity_id: uuid.UUID | None
    parent_node_id_list: List[str]
    is_suspendable: bool = False
    min_access_level: int | None = None


class ComponentDto(JsonOutModel):
    name: str = ""
    node_id: str = ""
    entity_id: uuid.UUID
    type: str = ""
    current_state: str | None = None
    skill_set: List[SkillDto] = []
    methods: List[MethodDto] = []
    monitoring: List[RemoteVariableDto] = []
    attributes: List[RemoteVariableDto] = []
    parameter_set: List[RemoteVariableDto] = []
    components: List["ComponentDto"] = []
    parent_entity_id: uuid.UUID | None
    parent_node_id_list: List[str]


class LockingModuleDto(JsonOutModel):
    is_enabled: bool
    is_simulated: bool
    is_locked: bool
    is_locked_since: str
    locking_user: str
    locking_client: str


class MachineDto(ComponentDto):
    locking_module: LockingModuleDto
