from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any

from asyncua import ua
from asyncua.common.node import Node
from asyncua.common.subscription import DataChangeEvent

from opensmi_ui.event.bus import EventBus
from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.action import GenericAction
from opensmi_ui.model.json import JsonInModel, JsonOutModel
from opensmi_ui.opc_model.entities.lock_entity import (
    LockEntity,
    LockIsLockedUpdate,
    LockLockingClientUpdate,
    LockLockingUserUpdate,
)
from opensmi_ui.opc_model.features.machinery_item_state_feature import FeatureInitState
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureNode,
    FeatureSubscribeDataRequest,
    FeatureSubscribeRequest,
)
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_model.opc_types import VariantData
from opensmi_ui.opc_model.value_read import (
    normalize_to_variant,
)

logger = get_module_logger("opc_model.features.lock")


class PossibleLockActions(StrEnum):
    INIT_LOCK = "InitLock"
    BREAK_LOCK = "BreakLock"
    EXIT_LOCK = "ExitLock"


class LockAction(JsonInModel):
    requested_action: PossibleLockActions


class LockFeatureInitData:
    nodes_to_read: list[OPCNode]


class LockFeatureNode(FeatureNode):
    _init_step: int
    _init_data: LockFeatureInitData

    action_nodes: dict[str, OPCNode]

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self._init_step = 0
        self.entity_type = "Lock"

        self._init_data = LockFeatureInitData()

        self.action_nodes = {}
        for child_node in opc_node.children:
            match child_node.browse_name.Name:
                case "InitLock" | "BreakLock" | "ExitLock" | "RenewLock":
                    self.action_nodes[child_node.browse_name.Name] = child_node

    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        match self._init_step:
            # Step 0
            case 0:
                self.init_state = FeatureInitState.PENDING

                try:
                    nodes_to_read = [
                        self.opc_node.get_first_child_node_for_name("Locked"),
                        self.opc_node.get_first_child_node_for_name("LockingUser"),
                        self.opc_node.get_first_child_node_for_name("LockingClient"),
                    ]

                    self._init_data.nodes_to_read = nodes_to_read

                    req = FeatureInitRequest(
                        browse_requests=[], read_requests=[], feature=self
                    )

                    for node_to_read in nodes_to_read:
                        req.read_requests.append(
                            ua.ReadValueId(
                                NodeId=node_to_read.node_id,
                                AttributeId=ua.attribute_ids.AttributeIds.Value,
                            )
                        )

                    self._init_step += 1
                    return req

                except KeyError as e:
                    self.init_state = FeatureInitState.ERROR
                    self.init_error = f"Missing node: {e!s}"

                    return None
            # Step 1
            case 1:
                try:
                    if last_result is None:
                        raise RuntimeError(
                            "Got unexpected none for last_result in LockFeature"
                        )

                    for idx, target_node in enumerate(self._init_data.nodes_to_read):
                        target_node.attributes["Value"] = last_result.read_results[
                            idx
                        ].Value
                        target_node.attributes["LastChange"] = last_result.read_results[
                            idx
                        ].SourceTimestamp

                    self.entity = LockEntity(opc_node=self.opc_node)

                    self._init_step += 1
                    self.init_state = FeatureInitState.DONE
                    return None
                except Exception as e:  # noqa: BLE001 # could be any exception
                    self.init_state = FeatureInitState.ERROR
                    self.init_error = str(e)
                    return None
            # catch all to always return None
            case _:
                return None

    def request_subscription(
        self, event_bus: EventBus
    ) -> FeatureSubscribeRequest | None:
        self.event_bus = event_bus

        req = FeatureSubscribeRequest(subscriptions=[])

        try:
            # locked_node = self.opc_node.get_first_child_node_for_name("Locked")
            items_to_sub_to = [
                (
                    self.opc_node.get_first_child_node_for_name("Locked"),
                    self.on_locked_update,
                ),
                (
                    self.opc_node.get_first_child_node_for_name("LockingUser"),
                    self.on_locking_user_update,
                ),
                (
                    self.opc_node.get_first_child_node_for_name("LockingClient"),
                    self.on_locking_client_update,
                ),
            ]

            for item in items_to_sub_to:
                req.subscriptions.append(
                    FeatureSubscribeDataRequest(
                        attr=ua.attribute_ids.AttributeIds.Value,
                        handler=item[1],
                        node_id=item[0].node_id,
                    )
                )

        except KeyError:
            logger.warning(
                "Failed to subscribe to Locked since no Locked node was present"
            )

        return req

    def _handle_update(
        self,
        evt: DataChangeEvent,
        callback: Callable[[Any, datetime | None], JsonOutModel],
    ):
        if not isinstance(self.entity, LockEntity):
            return

        try:
            data_value = evt.data.monitored_item.Value
            if not isinstance(data_value, ua.DataValue):
                logger.warning(
                    "Received unexpected Non-DataValue Update on LockFeature"
                )
                return

            value = normalize_to_variant(data_value)
            if not isinstance(value, ua.Variant):
                logger.warning("Received unexpected Non-Variant Update on LockFeature")
                return

            data = VariantData.from_ua(value)
            update = callback(data.value, (data_value.SourceTimestamp))

            self.entity.apply_update(update)
            if self.event_bus is not None:
                self.event_bus.publish(update)

        except Exception:
            logger.exception("Failed to handle Update due to an Exception")
            return

    def on_locked_update(self, node: Node, evt: DataChangeEvent):
        self._handle_update(
            evt,
            lambda val, timestamp: LockIsLockedUpdate(
                entity_id=self.entity_id,
                new_is_locked=val,
                timestamp=str(timestamp),
            ),
        )

    def on_locking_user_update(self, node: Node, evt: DataChangeEvent):
        self._handle_update(
            evt,
            lambda val, timestamp: LockLockingUserUpdate(
                entity_id=self.entity_id,
                new_user=val,
                timestamp=str(timestamp),
            ),
        )

    def on_locking_client_update(self, node: Node, evt: DataChangeEvent):
        self._handle_update(
            evt,
            lambda val, timestamp: LockLockingClientUpdate(
                entity_id=self.entity_id,
                new_client=val,
                timestamp=str(timestamp),
            ),
        )

    async def handle_action(self, action: GenericAction) -> None:
        method_node_to_call: OPCNode | None = None
        match action.action_type:
            case "LockAction":
                data = LockAction.model_validate(action.action)
                method_node_to_call = self.action_nodes.get(
                    data.requested_action.value, None
                )
            case _:
                logger.warning(
                    f"received unsupported Action of type {action.action_type} on LockFeature"
                )
                return

        if method_node_to_call is None:
            raise RuntimeError(
                f"Cannot complete Action {action.action_type} because the desired Node is not present"
            )

        await self.opc_node.ua_node.call_method(methodid=method_node_to_call.node_id)
