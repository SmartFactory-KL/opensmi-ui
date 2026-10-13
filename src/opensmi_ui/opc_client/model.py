from collections import deque
from dataclasses import dataclass

from opensmi.client import (
    BaseRemoteComponent,
    RemoteMethod,
    RemoteServer,
    RemoteSkill,
)
from opensmi.client.dto import RemoteUaObjectDTO
from opensmi.client.remote_lock import RemoteLock
from opensmi.client.remote_resource import RemoteResource
from opensmi.client.remote_user import RemoteUser
from opensmi.client.remote_variable_container import RemoteVariableContainer
from opensmi.core.base_ua_object import PurePosixPath

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


class FeatureSetEntityDTO(RemoteUaObjectDTO): ...


class FeatureSetEntity:
    name: str
    path: PurePosixPath
    ua_node_id: str
    ua_type: str

    def __init__(
        self,
        name: str | None = None,
        path: PurePosixPath | None = None,
        ua_node_id: str | None = None,
        ua_type: str | None = None,
    ):
        self.name = name if name is not None else "FeatureSet"
        self.path = path if path is not None else PurePosixPath()
        self.ua_node_id = ua_node_id if ua_node_id is not None else ""
        self.ua_type = ua_type if ua_type is not None else "unknown"

    def dto(self) -> FeatureSetEntityDTO:
        return FeatureSetEntityDTO(
            name=self.name,
            path=self.path,
            ua_node_id=self.ua_node_id,
            ua_type=self.ua_type,
        )


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

        component_queue = deque(self.root_components)

        while component_queue:
            next_component = component_queue.popleft()

            if not isinstance(next_component, ComponentEntity) or not isinstance(
                next_component.entity, BaseRemoteComponent
            ):
                continue

            # attach to components own signals
            next_component.entity.status_changed.connect(
                receiver.receive_component_state
            )
            next_component.entity.notification_received.connect(
                receiver.receive_component_notification
            )

            for feature in next_component.features:
                match feature.entity_type:
                    case "RemoteLock":
                        if not isinstance(feature.entity, RemoteLock):
                            logger.info(
                                f"skipped entity because type {type(feature.entity)} is not expected type {RemoteLock}"
                            )
                            continue

                        feature.entity.locked_changed.connect(
                            receiver.receive_lock_changed
                        )
                        feature.entity.locking_user_changed.connect(
                            receiver.receive_lock_user_changed
                        )

                    case "Identification" | "Attributes" | "Monitoring" | "ParameterSet" | "FinalResultDataSet":
                        if not isinstance(feature.entity, RemoteVariableContainer):
                            logger.info(
                                f"skipped entity because type {type(feature.entity)} is not expected type {RemoteVariableContainer}"
                            )
                            continue

                        for variable in feature.entity:
                            variable.value_changed.connect(
                                receiver.receive_value_changed
                            )


# #########################################################################################


def create_features(entity: DTOEntity) -> list[FeatureEntity]:
    if not isinstance(entity, BaseRemoteComponent):
        return []

    result: list[FeatureEntity] = []

    # These are features that are directly available as a DTOEntity
    # The tuple contains: (attribute_name, expected_type)
    features_to_check: list[tuple[str, type]] = [
        ("lock", RemoteLock),
        ("attributes", RemoteVariableContainer),
        ("identification", RemoteVariableContainer),
        ("monitoring", RemoteVariableContainer),
        ("parameter_set", RemoteVariableContainer),
    ]

    # check non-list attributes
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

        result.append(FeatureEntity(entity=attr))

    # These features have no direct DTOEntity, so they must be handled in lists
    # The tuple contains: (attribute_name, expected_type, expected_type_of_all_elements, target_dto_entity_container)
    listable_features_to_check: list[tuple[str, type, type]] = [
        ("skill_set", dict, RemoteSkill),
        ("feasibility_check_set", dict, RemoteSkill),
        ("precondition_check_set", dict, RemoteSkill),
        ("method_set", dict, RemoteMethod),
        ("resources", dict, RemoteResource),
        ("users", list, RemoteUser),
    ]

    for feat_name, list_type, feat_type in listable_features_to_check:
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

        set_feature = FeatureEntity(entity=FeatureSetEntity(name=feat_name))

        for val in elements:
            set_feature.append_feature(FeatureEntity(entity=val))

        result.append(set_feature)

    return result
