from abc import abstractmethod
from typing import Protocol, override
from uuid import UUID, uuid4

from opensmi.client.dto import (
    RemoteCallableDTO,
    RemoteComponentDTO,
    RemoteLockDTO,
    RemoteMachineDTO,
    RemoteResourceDTO,
    RemoteSkillDTO,
    RemoteUaObjectDTO,
    RemoteUserDTO,
    RemoteVariableDTO,
)

from opensmi_ui.model.common import JsonOutModel


class DTOEntity(Protocol):
    def dto(self) -> RemoteUaObjectDTO: ...


class ComponentDataDTO(RemoteUaObjectDTO):
    current_state: str


class FeatureEntityDTO(JsonOutModel):
    entity_id: UUID
    entity_type: str

    data: (
        RemoteMachineDTO
        | RemoteComponentDTO
        | RemoteLockDTO
        | RemoteResourceDTO
        | RemoteSkillDTO
        | RemoteCallableDTO
        | list[RemoteVariableDTO]
        | RemoteVariableDTO
        | RemoteUserDTO
        | RemoteUaObjectDTO
    )


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
