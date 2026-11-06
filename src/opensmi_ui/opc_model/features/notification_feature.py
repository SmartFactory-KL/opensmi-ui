from asyncua.common.events import Event

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.notification_entity import NotificationEntity
from opensmi_ui.opc_model.feature_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
    FeatureSubscribeEventRequest,
    FeatureSubscribeRequest,
)
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_session.namespace import OPCNamespace
from opensmi_ui.opc_subscriber.notification import read_notification

logger = get_module_logger("opc_model.features.notification")


class NotificationFeatureNode(FeatureNode):
    def __init__(
        self,
        opc_node: OPCNode,
        opc_namespace: OPCNamespace,
        parent_component_node: ComponentNode,
    ):
        super().__init__(
            opc_node=opc_node,
            opc_namespace=opc_namespace,
            parent_component_node=parent_component_node,
        )
        self.entity_type = "Notification"

    def _populate_step(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        self.entity = NotificationEntity(opc_node=self.opc_node)
        self.init_state = FeatureInitState.DONE
        return None

    def _request_subscription(self) -> FeatureSubscribeRequest | None:
        req = FeatureSubscribeRequest(subscriptions=[])

        # check if a messages node exists
        messages_node = self.opc_node
        try:
            messages_node = self.opc_node.get_first_child_node_for_name("Messages")
        except KeyError:
            pass

        req.subscriptions.append(
            FeatureSubscribeEventRequest(
                handler=self.on_notification,
                feature=self,
                node_id=messages_node.node_id,
            )
        )

        return req

    def on_notification(self, evt: Event):
        if self.event_bus is None:
            return

        try:
            notification = read_notification(
                event=evt, opc_namespace=self.opc_namespace
            )
            if notification is None:
                return

            self.event_bus.publish(notification)
        except Exception:
            logger.exception("Failed to convert OpcEvent to Notification")
