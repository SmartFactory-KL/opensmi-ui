from asyncua import ua
from asyncua.common.node import Node
from asyncua.common.subscription import DataChangeEvent

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.entities.user_entity import UserEntity, UserIsPresentUpdate
from opensmi_ui.opc_model.feature_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
    FeatureSubscribeDataRequest,
    FeatureSubscribeRequest,
)
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_model.update import handle_update_with_callback
from opensmi_ui.opc_session.namespace import OPCNamespace

logger = get_module_logger("opc_model.features.user")


class UserFeatureNode(FeatureNode):
    _init_step: int

    def __init__(
        self,
        opc_node: OPCNode,
        opc_namespace: OPCNamespace,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(
            opc_node=opc_node,
            opc_namespace=opc_namespace,
            parent_component_node=parent_component_node,
            parent_feature_node=parent_feature_node,
        )
        self._init_step = 0
        self.entity_type = "User"

    def _populate_step(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        match self._init_step:
            case 0:
                self.init_state = FeatureInitState.PENDING

                req = FeatureInitRequest(
                    browse_requests=[], read_requests=[], feature=self
                )

                for child in self.opc_node.children:
                    req.read_requests.append(
                        ua.ReadValueId(
                            NodeId=child.node_id,
                            AttributeId=ua.attribute_ids.AttributeIds.Value,
                        )
                    )

                self._init_step += 1

                return req
            case 1:
                if last_result is None:
                    raise ValueError(
                        f"Received Unexpected None Result for step {self._init_step}"
                    )

                for idx, child in enumerate(self.opc_node.children):
                    match child.browse_name.Name:
                        case (
                            "AllowMultiple"
                            | "UserLevel"
                            | "MaxAccessLevel"
                            | "IsPresent"
                        ):
                            cur_result = last_result.read_results[idx]

                            if (
                                cur_result.StatusCode is None
                                or cur_result.StatusCode.is_bad()
                            ):
                                continue

                            child.attributes["Value"] = cur_result.Value

                self.entity = UserEntity(opc_node=self.opc_node)

                self._init_step += 1
                self.init_state = FeatureInitState.DONE

                return None
            case _:
                return None

    def _request_subscription(self) -> FeatureSubscribeRequest | None:
        req = FeatureSubscribeRequest(subscriptions=[])

        is_present_node = self.opc_node.get_first_child_node_for_name("IsPresent")

        req.subscriptions.append(
            FeatureSubscribeDataRequest(
                attr=ua.attribute_ids.AttributeIds.Value,
                feature=self,
                handler=self.on_is_present_update,
                node_id=is_present_node.node_id,
            )
        )

        return req

    def on_is_present_update(self, node: Node, evt: DataChangeEvent) -> None:
        if not isinstance(self.entity, UserEntity):
            return

        try:
            handle_update_with_callback(
                evt=evt,
                update_creator=lambda val, timestamp: UserIsPresentUpdate(
                    entity_id=self.entity_id,
                    new_is_present=val,
                    timestamp=str(timestamp),
                ),
                entity=self.entity,
                callback=self.publish_update,
            )
        except Exception:
            logger.exception("Failed to handle IsPresent Update on UserFeature")

    def publish_update(self, update: JsonOutModel):
        if self.event_bus is not None:
            self.event_bus.publish(update)
