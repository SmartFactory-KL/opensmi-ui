from abc import abstractmethod
from dataclasses import fields, is_dataclass
from pathlib import PurePath
from typing import Any, Protocol, override, runtime_checkable
from uuid import UUID, uuid4

from pydantic import field_serializer
from pydantic.alias_generators import to_camel

from opensmi_ui.model.common import JsonOutModel


def to_json_compatible(value: Any) -> Any:
    """Converts any input to serializable content

    Currently mostly for PurePosixPath, because Pydantic fails to serialize it
    whenever its used as part of an "Any" object
    """
    if isinstance(value, PurePath):
        return str(value)

    if is_dataclass(value) and not isinstance(value, type):
        return {
            to_camel(field.name): to_json_compatible(getattr(value, field.name))
            for field in fields(value)
        }

    if isinstance(value, dict):
        return {key: to_json_compatible(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [to_json_compatible(item) for item in value]

    return value


@runtime_checkable
class DTOEntity(Protocol):
    def dto(self) -> object: ...


class FeatureEntityDTO(JsonOutModel):
    entity_id: UUID
    entity_type: str

    data: Any

    features: list["FeatureEntityDTO"]

    @field_serializer("data", when_used="json")
    def serialize_data(self, value: object) -> Any:
        return to_json_compatible(value)


class ComponentEntityDTO(FeatureEntityDTO):
    children: list["ComponentEntityDTO"]


class FeatureEntity:
    entity_id: UUID
    entity: DTOEntity
    entity_type: str

    features: list["FeatureEntity"]

    def __init__(self, entity: DTOEntity):
        self.entity_id = uuid4()
        self.entity = entity
        self.entity_type = type(entity).__name__

        self.features = []

    def append_feature(self, feature: "FeatureEntity"):
        self.features.append(feature)

    def get_feature_dtos(self) -> list[FeatureEntityDTO]:
        feature_dtos: list[FeatureEntityDTO] = []

        if self.features is not None:
            feature_dtos = []
            for feature in self.features:
                feature_dtos.append(feature.dto())

        return feature_dtos

    @abstractmethod
    def dto(self) -> FeatureEntityDTO:
        return FeatureEntityDTO(
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            data=self.entity.dto(),
            features=self.get_feature_dtos(),
        )


class ComponentEntity(FeatureEntity):
    # all child components
    children: list["ComponentEntity"]

    def __init__(self, entity: DTOEntity):
        super().__init__(entity=entity)

        self.children = []

    @override
    def dto(self) -> ComponentEntityDTO:
        return ComponentEntityDTO(
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            data=self.entity.dto(),
            children=[child.dto() for child in self.children],
            features=self.get_feature_dtos(),
        )
