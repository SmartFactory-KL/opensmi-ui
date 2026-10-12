from collections import deque
from dataclasses import dataclass

from opensmi.client import (
    BaseRemoteComponent,
    RemoteMethod,
    RemoteServer,
    RemoteSkill,
)
from opensmi.client.remote_lock import RemoteLock
from opensmi.client.remote_resource import RemoteResource
from opensmi.client.remote_user import RemoteUser
from opensmi.client.remote_variable_container import RemoteVariableContainer

from opensmi_ui.logger import get_module_logger
from opensmi_ui.messages.receiver import MessageReceiver
from opensmi_ui.opc_client.identifiable import (
    ComponentEntity,
    ComponentEntityDTO,
    DTOContainerEntity,
    DTOEntity,
    FeatureEntity,
    MethodSetEntity,
    ResourceSetEntity,
    SkillSetEntity,
    UserSetEntity,
)

logger = get_module_logger("opc_client.model")


@dataclass(frozen=True)
class QueueItem:
    entity: DTOEntity
    parent_entity: ComponentEntity | None


class MachineryModel:
    root_components: list[ComponentEntity]

    def __init__(self):
        self.root_components = []

    def get_component_dtos(self) -> list[ComponentEntityDTO]:
        result: list[ComponentEntityDTO] = []

        for root_component in self.root_components:
            result.append(root_component.dto())

        return result

    def create_from_client(self, client: RemoteServer) -> None:
        machines = client.machines

        component_queue = deque[QueueItem](
            [
                QueueItem(entity=entity, parent_entity=None)
                for entity in machines.values()
            ]
        )

        root_component_entities: list[ComponentEntity] = []

        while component_queue:
            next_item = component_queue.popleft()
            next_entity = next_item.entity

            next_component_entity = ComponentEntity(entity=next_entity)

            # Add Features
            next_component_entity.features = create_features(entity=next_entity)

            if next_item.parent_entity is None:
                root_component_entities.append(next_component_entity)
            else:
                next_item.parent_entity.children.append(next_component_entity)

            # Handle Children
            if isinstance(next_entity, BaseRemoteComponent):
                for child in next_entity.components.values():
                    component_queue.append(
                        QueueItem(entity=child, parent_entity=next_component_entity)
                    )

        self.root_components = root_component_entities

    def connect_signals(self, receiver: MessageReceiver) -> None:
        if not len(self.root_components):
            return


def create_features(entity: DTOEntity) -> list[FeatureEntity]:
    if not isinstance(entity, BaseRemoteComponent):
        return []

    result: list[FeatureEntity] = []
    dto_entities: list[DTOEntity] = []

    # These are features that are directly available as a DTOEntity
    # The tuple contains: (attribute_name, expected_type)
    features_to_check: list[tuple[str, type]] = [
        ("lock", RemoteLock),
        ("attributes", RemoteVariableContainer),
        ("identification", RemoteVariableContainer),
        ("monitoring", RemoteVariableContainer),
        ("parameter_set", RemoteVariableContainer),
    ]

    skill_set_container = SkillSetEntity()
    method_set_container = MethodSetEntity()
    resources_container = ResourceSetEntity()
    users_container = UserSetEntity()

    # These features have no direct DTOEntity, so they must be handled in lists
    # The tuple contains: (attribute_name, expected_type, expected_type_of_all_elements, target_dto_entity_container)
    listable_features_to_check: list[tuple[str, type, type, DTOContainerEntity]] = [
        ("skill_set", dict, RemoteSkill, skill_set_container),
        ("feasibility_check_set", dict, RemoteSkill, skill_set_container),
        ("precondition_check_set", dict, RemoteSkill, skill_set_container),
        ("method_set", dict, RemoteMethod, method_set_container),
        ("resources", dict, RemoteResource, resources_container),
        ("users", list, RemoteUser, users_container),
    ]

    for feat_name, feat_type in features_to_check:
        attr = getattr(entity, feat_name, None)

        if attr is None:
            continue

        if not isinstance(attr, feat_type):
            logger.info(
                f"type mismatch on features: expected {feat_type} but got {type(attr)} for {feat_name}"
            )
            continue

        if not isinstance(attr, DTOEntity):
            logger.info(
                f"type mismatch on features: expected {feat_type} to be of type DTOEntity but it was not for {feat_name}"
            )
            continue

        dto_entities.append(attr)

    for feat_name, list_type, feat_type, target_container in listable_features_to_check:
        attr = getattr(entity, feat_name, None)

        if attr is None:
            continue

        if not isinstance(attr, list_type):
            logger.info(
                f"type mismatch on listable features: expected list_type {feat_type} but got {type(attr)} for {feat_name}"
            )
            continue

        elements = []
        if list_type is list:
            elements = attr
        elif list_type is dict:
            elements = attr.values()

        all_elements_ok = True
        for idx, val in enumerate(elements):
            if not isinstance(val, feat_type):
                logger.info(
                    f"type mismatch on listable features details: expected feat_type {feat_type} but got {type(val)} for {feat_name} # {idx}"
                )
                all_elements_ok = False
                break

        if not all_elements_ok:
            continue

        # all checks passed
        for val in elements:
            target_container.add_item(val)

        if target_container not in dto_entities:
            dto_entities.append(target_container)

    for dto_entity in dto_entities:
        result.append(FeatureEntity(entity=dto_entity))

    return result
