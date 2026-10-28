from time import perf_counter
from uuid import UUID

from asyncua import ua

from opensmi_ui.event.bus import EventBus
from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.action import GenericAction
from opensmi_ui.opc_model.browser import OPCBrowser
from opensmi_ui.opc_model.feature_node import (
    ComponentNode,
    ComponentNodeData,
    FeatureNode,
    FeatureSubscribeDataRequest,
    FeatureSubscribeEventRequest,
    FeatureSubscribeRequest,
    FeatureValueReadRequest,
    FeatureValueReadResult,
    visit_tree_features,
)
from opensmi_ui.opc_subscriber.subscriber import (
    OPCSubscriber,
    SubscribeDataRequest,
    SubscribeEventRequest,
    SubscriptionHandles,
)

logger = get_module_logger("opc_model.model")


class OPCModel:
    opc_browser: OPCBrowser

    last_subscription_handles: SubscriptionHandles
    event_bus: EventBus

    root_component_nodes: list[ComponentNode]
    entity_id_feature_map: dict[UUID, FeatureNode]

    def __init__(self, opc_browser: OPCBrowser):
        self.opc_browser = opc_browser
        self.last_subscription_handles = SubscriptionHandles(
            data_change_handles=[], event_handles=[]
        )
        self.event_bus = EventBus()

        self.root_component_nodes = []
        self.entity_id_feature_map = {}

    async def browse_model(self):
        self.entity_id_feature_map.clear()

        result = await self.opc_browser.read_model()

        def add_entity_ref(feature: FeatureNode, component: ComponentNode):
            self.entity_id_feature_map[feature.entity_id] = feature

        for root_component_node in result:
            visit_tree_features(root_component_node, add_entity_ref)

        self.root_component_nodes = result

    async def discard_old_subscriptions(self, opc_subscriber: OPCSubscriber):
        if len(self.last_subscription_handles.data_change_handles) > 0 or (
            len(self.last_subscription_handles.event_handles) > 0
        ):
            logger.info(
                "Clearing old subscriptions: %d data_change and %d events",
                len(self.last_subscription_handles.data_change_handles),
                len(self.last_subscription_handles.event_handles),
            )
            try:
                await opc_subscriber.clear_subscription_handles(
                    self.last_subscription_handles
                )
                logger.info("Clearing old subscriptions finished")
            except RuntimeError as e:
                logger.warning("Failed to clear old subscriptions: %s", str(e))

    async def attach_subscriptions(self, opc_subscriber: OPCSubscriber):
        # create subscriptions
        sub_init_start = perf_counter()
        sub_requests: list[FeatureSubscribeRequest] = []

        def read_sub(feature: FeatureNode, _) -> None:
            req = feature.request_subscription(self.event_bus)
            if req is not None:
                sub_requests.append(req)

        for root_node in self.root_component_nodes:
            visit_tree_features(tree=root_node, method=read_sub)

        subs_to_create: list[SubscribeDataRequest | SubscribeEventRequest] = []
        for sub_request in sub_requests:
            for sub in sub_request.subscriptions:
                if isinstance(sub, FeatureSubscribeDataRequest):
                    subs_to_create.append(
                        SubscribeDataRequest(
                            attr=sub.attr,
                            handler=sub.handler,
                            node_id=sub.node_id,
                            on_fail=sub.feature.handle_subscription_failure,
                        )
                    )
                elif isinstance(sub, FeatureSubscribeEventRequest):
                    subs_to_create.append(
                        SubscribeEventRequest(
                            handler=sub.handler,
                            node_id=sub.node_id,
                            on_fail=sub.feature.handle_subscription_failure,
                        )
                    )
                else:
                    continue

        result_handles = await opc_subscriber.add_subscription_batch(subs_to_create)
        self.last_subscription_handles = result_handles

        sub_init_duration = perf_counter() - sub_init_start
        logger.info("Subscription Requesting took %.6f seconds", sub_init_duration)

    async def attach_values(self):
        # final attribute read run
        val_read_start = perf_counter()
        feat_val_read_requests: list[FeatureValueReadRequest] = []

        def read_val_request(feature: FeatureNode, _) -> None:
            req = feature.request_value()
            if req is not None:
                feat_val_read_requests.append(req)

        for root_node in self.root_component_nodes:
            visit_tree_features(tree=root_node, method=read_val_request)

        read_value_list: list[ua.ReadValueId] = []
        for feat_read_request in feat_val_read_requests:
            read_value_list.extend(feat_read_request.read_requests)

        reading_results = await self.opc_browser.read_requests_in_chunks(
            reading_requests=read_value_list
        )

        result_idx = 0
        for feat_read_request in feat_val_read_requests:
            _size = len(feat_read_request.read_requests)

            feat_results = reading_results[result_idx : (result_idx + _size)]

            feat_read_request.feature.handle_value_result(
                FeatureValueReadResult(read_results=feat_results)
            )

            result_idx += _size

        val_read_duration = perf_counter() - val_read_start
        logger.info("Reading Values took %.6f seconds", val_read_duration)

    async def proxy_action(self, action: GenericAction) -> None:
        target_entity_id = action.entity_id

        target_feature = self.entity_id_feature_map.get(target_entity_id, None)
        if target_feature is None:
            raise KeyError(f"No Feature found for entityId {target_entity_id}")

        await target_feature.handle_action(action)

    def get_data(self):
        # convert to serializables
        root_node_list: list[ComponentNodeData] = []
        for root_node in self.root_component_nodes:
            root_node_list.append(root_node.get_data())

        return root_node_list
