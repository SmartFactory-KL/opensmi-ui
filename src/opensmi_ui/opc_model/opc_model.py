from time import perf_counter

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.browser import OPCBrowser
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    ComponentNodeData,
    FeatureNode,
    FeatureSubscribeDataRequest,
    FeatureSubscribeEventRequest,
    FeatureSubscribeRequest,
    visit_tree_features,
)
from opensmi_ui.opc_subscriber.subscriber import (
    OPCSubscriber,
    SubscribeDataRequest,
    SubscribeEventRequest,
)

logger = get_module_logger("opc_model.model")


class OPCModel:
    opc_browser: OPCBrowser

    root_component_nodes: list[ComponentNode]

    def __init__(self, opc_browser: OPCBrowser):
        self.opc_browser = opc_browser

        self.root_component_nodes = []

    async def browse_model(self):
        result = await self.opc_browser.read_model()
        self.root_component_nodes = result

    async def attach_subscriptions(self, opc_subscriber: OPCSubscriber):
        # create subscriptions
        sub_init_start = perf_counter()
        sub_requests: list[FeatureSubscribeRequest] = []

        def read_sub(feature: FeatureNode, _) -> None:
            req = feature.subscribe()
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
                        )
                    )
                elif isinstance(sub, FeatureSubscribeEventRequest):
                    subs_to_create.append(
                        SubscribeEventRequest(
                            handler=sub.handler,
                            node_id=sub.node_id,
                        )
                    )
                else:
                    continue

        await opc_subscriber.add_subscription_batch(subs_to_create)

        sub_init_duration = perf_counter() - sub_init_start
        logger.info("Subscription Requesting took %.6f seconds", sub_init_duration)

    def get_data(self):
        # convert to serializables
        root_node_list: list[ComponentNodeData] = []
        for root_node in self.root_component_nodes:
            root_node_list.append(root_node.get_data())

        return root_node_list
