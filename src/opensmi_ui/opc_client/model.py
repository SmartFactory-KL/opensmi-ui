from collections import deque
from dataclasses import dataclass
from uuid import uuid4

from opensmi.client import (
    BaseRemoteComponent,
    RemoteMethod,
    RemoteServer,
    RemoteSkill,
    RemoteVariable,
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
    DTOEntity,
    FeatureEntity,
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

    features_to_check: list[tuple[str, type, type | None]] = [
        ("lock", RemoteLock, None),
        ("attributes", RemoteVariableContainer, None),
        ("identification", RemoteVariableContainer, None),
        ("monitoring", RemoteVariableContainer, None),
        ("parameter_set", RemoteVariableContainer, None),
        ("skill_set", dict, RemoteSkill),
        ("method_set", dict, RemoteMethod),
        ("resources", dict, RemoteResource),
        ("users", list, RemoteUser),
    ]

    for feat_name, feat_type, feat_detail_type in features_to_check:
        attr = getattr(entity, feat_name, None)

        if attr is None:
            continue

        if not isinstance(attr, feat_type):
            logger.info(
                f"type mismatch on features: expected {feat_type} but got {type(attr)} for {feat_name}"
            )
            continue

        if (feat_type is dict or feat_type is list) and feat_detail_type is not None:
            all_ok = True

            elements = []
            if feat_type is dict:
                elements = list(attr.values())
            elif feat_type is list:
                elements = attr

            for val in elements:
                if not isinstance(val, feat_detail_type):
                    logger.info(
                        f"type mismatch on features detail: expected {feat_type} but got {type(attr)} for {feat_name}"
                    )
                    all_ok = False
                    break
            if not all_ok:
                continue

        # up until here all were just checks
        if feat_type is dict:
            for val in attr.values():
                result.append(FeatureEntity(entity=val))
        elif feat_type is list:
            for val in attr:
                result.append(FeatureEntity(entity=val))
        else:
            result.append(FeatureEntity(entity=attr))

    return result


def _add_var_container_references(self, variable: RemoteVariable):
    vars_to_process = deque[RemoteVariable]([variable])

    while vars_to_process:
        var_to_process = vars_to_process.popleft()
        self._variable_cache.add(uuid4(), var_to_process)

        var_to_process.value_changed.connect(self.receiver.receive_value_changed)

        for var_child in var_to_process.children.values():
            vars_to_process.append(var_child)
