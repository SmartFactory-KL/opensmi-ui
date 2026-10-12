from abc import abstractmethod
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Protocol, TypeVar, override, runtime_checkable
from uuid import UUID, uuid4

from opensmi.client import RemoteMethod, RemoteResource, RemoteSkill, RemoteUser
from opensmi.client.dto import RemoteUaObjectDTO

from opensmi_ui.model.common import JsonOutModel


@runtime_checkable
class DTOEntity(Protocol):
    def dto(self) -> object: ...


@dataclass(slots=True, frozen=True, kw_only=True)
class ComponentDataDTO(RemoteUaObjectDTO):
    current_state: str


@dataclass(slots=True, frozen=True, kw_only=True)
class DTOContainerEntityDTO(RemoteUaObjectDTO):
    list_type: str
    items: list[RemoteUaObjectDTO]


class FeatureEntityDTO(JsonOutModel):
    entity_id: UUID
    entity_type: str

    data: object


class ComponentEntityDTO(FeatureEntityDTO):
    features: list[FeatureEntityDTO]
    children: list["ComponentEntityDTO"]


class FeatureEntity:
    entity_id: UUID
    entity: DTOEntity
    entity_type: str

    def __init__(self, entity: DTOEntity):
        self.entity_id = uuid4()
        self.entity = entity
        self.entity_type = type(entity).__name__

    @abstractmethod
    def dto(self) -> FeatureEntityDTO:
        return FeatureEntityDTO(
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            data=self.entity.dto(),
        )


class DTOContainerEntity[T: DTOEntity]:
    def __init__(self):
        self.list_type = str(T)
        self.items: list[T] = []

    def add_item(self, item: T):
        self.items.append(item)

    def dto(
        self,
    ) -> DTOContainerEntityDTO:
        return DTOContainerEntityDTO(
            name="None",
            path=PurePosixPath(""),
            ua_node_id="None",
            ua_type="None",
            list_type=self.list_type,
            items=[item.dto() for item in self.items],
        )


class SkillSetEntity(DTOContainerEntity[RemoteSkill]): ...


class MethodSetEntity(DTOContainerEntity[RemoteMethod]): ...


class ResourceSetEntity(DTOContainerEntity[RemoteResource]): ...


class UserSetEntity(DTOContainerEntity[RemoteUser]): ...


class ComponentEntity(FeatureEntity):
    # all non-component entities
    features: list[FeatureEntity]

    # all child components
    children: list["ComponentEntity"]

    def __init__(self, entity: DTOEntity):
        super().__init__(entity=entity)

        self.features = []
        self.children = []

    @override
    def dto(self) -> ComponentEntityDTO:
        return ComponentEntityDTO(
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            data=self.entity.dto(),
            children=[child.dto() for child in self.children],
            features=[feature.dto() for feature in self.features],
        )
