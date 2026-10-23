from asyncua.common.events import Event

from opensmi_ui.event.bus import EventBus
from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.notification_entity import NotificationEntity
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
    FeatureSubscribeEventRequest,
    FeatureSubscribeRequest,
)
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_subscriber.notification import read_notification

logger = get_module_logger("opc_model.features.notification")


class NotificationFeatureNode(FeatureNode):
    def __init__(self, opc_node: OPCNode, parent_component_node: ComponentNode):
        super().__init__(opc_node=opc_node, parent_component_node=parent_component_node)
        self.entity_type = "Notification"

    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        self.entity = NotificationEntity(opc_node=self.opc_node)
        self.init_state = FeatureInitState.DONE
        return None

    def request_subscription(
        self, event_bus: EventBus
    ) -> FeatureSubscribeRequest | None:
        self.event_bus = event_bus

        req = FeatureSubscribeRequest(subscriptions=[])

        req.subscriptions.append(
            FeatureSubscribeEventRequest(
                handler=self.on_notification, node_id=self.opc_node.node_id
            )
        )

        return req

    def on_notification(self, evt: Event):
        if self.event_bus is None:
            return

        try:
            notification = read_notification(evt)
            if notification is None:
                return

            self.event_bus.publish(notification)
        except Exception:
            logger.exception("Failed to convert OpcEvent to Notification")
