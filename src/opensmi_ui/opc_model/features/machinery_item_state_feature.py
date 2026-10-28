from asyncua import ua
from asyncua.common.node import Node
from asyncua.common.subscription import DataChangeEvent

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.machinery_item_state_entity import (
    MachineryItemStateEntity,
)
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
from opensmi_ui.opc_model.value_read import read_data_change_event_value

logger = get_module_logger("opc_model.features.resource")


class MachineryItemStateFeatureNode(FeatureNode):
    _init_step: int

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self._init_step = 0
        self.entity_type = "MachineryItemState"

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
                    val_result = last_result.read_results[idx]

                    if val_result.StatusCode is None or val_result.StatusCode.is_bad():
                        continue

                    if val_result.Value is not None:
                        child.attributes["Value"] = val_result.Value.Value

                self.entity = MachineryItemStateEntity(opc_node=self.opc_node)

                self._init_step += 1
                self.init_state = FeatureInitState.DONE

                return None
            case _:
                return None

    def _request_subscription(self) -> FeatureSubscribeRequest | None:
        req = FeatureSubscribeRequest(subscriptions=[])

        req.subscriptions.append(
            FeatureSubscribeDataRequest(
                attr=ua.attribute_ids.AttributeIds.Value,
                feature=self,
                handler=self.on_state_update,
                node_id=self.opc_node.node_id,
            )
        )

        return req

    def on_state_update(self, node: Node, evt: DataChangeEvent):
        if not isinstance(self.entity, MachineryItemStateEntity):
            return

        try:
            value = read_data_change_event_value(evt)
            # data_value = evt.data.monitored_item.Value

            logger.info("MachineryItemState: %s", value)

        except Exception:
            logger.exception("Failed to handle update of MachineryItemState")
            return
