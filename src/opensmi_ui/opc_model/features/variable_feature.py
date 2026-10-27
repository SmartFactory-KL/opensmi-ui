from typing import Any
from uuid import UUID

from asyncua import ua
from asyncua.common.node import Node
from asyncua.common.subscription import DataChangeEvent

from opensmi_ui.event.bus import EventBus
from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.json import JsonInModel, JsonOutModel
from opensmi_ui.opc_model.entities.variable_entity import VariableEntity
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
    FeatureSubscribeDataRequest,
    FeatureSubscribeRequest,
    FeatureValueReadRequest,
    FeatureValueReadResult,
)
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_model.opc_types import VariantData
from opensmi_ui.opc_model.value_read import (
    VariantNormalizationFailedError,
    normalize_to_variant,
)

logger = get_module_logger("opc_model.features.variable")

HAS_PROPERTY_REFERENCE = ua.NodeId(
    ua.Int32(ua.object_ids.ObjectIds.HasProperty), ua.Int16(0)
)


ATTRIBUTES_TO_READ = [
    # already present
    # ua.attribute_ids.AttributeIds.NodeId,
    # ua.attribute_ids.AttributeIds.NodeClass,
    # ua.attribute_ids.AttributeIds.BrowseName,
    # ua.attribute_ids.AttributeIds.DisplayName,
    ua.attribute_ids.AttributeIds.Description,
    # will be read separately at the end
    ua.attribute_ids.AttributeIds.Value,
    ua.attribute_ids.AttributeIds.DataType,
    ua.attribute_ids.AttributeIds.ValueRank,
    ua.attribute_ids.AttributeIds.ArrayDimensions,
    ua.attribute_ids.AttributeIds.AccessLevel,
    ua.attribute_ids.AttributeIds.UserAccessLevel,
    # probably not interesting as of now
    ua.attribute_ids.AttributeIds.MinimumSamplingInterval,
    ua.attribute_ids.AttributeIds.Historizing,
    ua.attribute_ids.AttributeIds.WriteMask,
    ua.attribute_ids.AttributeIds.UserWriteMask,
    ua.attribute_ids.AttributeIds.RolePermissions,
    ua.attribute_ids.AttributeIds.UserRolePermissions,
    ua.attribute_ids.AttributeIds.AccessRestrictions,
    ua.attribute_ids.AttributeIds.EventNotifier,
]


class VariableValueUpdate(JsonOutModel):
    entity_id: UUID
    new_value: Any


class VariableSetValueAction(JsonInModel):
    new_value: Any


class VariableFeatureNode(FeatureNode):
    _init_step: int

    properties_to_read: list[OPCNode]

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self._init_step = 0
        self.entity_type = "Variable"

        self.properties_to_read = []

    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        try:
            match self._init_step:
                case 0:
                    return self._advance_step_0(last_result)
                case 1:
                    return self._advance_step_1(last_result)
                case _:
                    return None
        except Exception as e:  # noqa: BLE001 # catch all to prevent silent fails on features
            self.init_state = FeatureInitState.ERROR
            self.init_error = str(e)
            return None

    def _advance_step_0(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        self.init_state = FeatureInitState.PENDING

        # first step is to read the attributes and browse properties that are available
        req = FeatureInitRequest(browse_requests=[], read_requests=[], feature=self)

        for attr_result in ATTRIBUTES_TO_READ:
            req.read_requests.append(
                ua.ReadValueId(NodeId=self.opc_node.node_id, AttributeId=attr_result)
            )

        # check for properties to read their value as well
        self.properties_to_read = []
        for child in self.opc_node.children:
            if (
                child.reference_type is not None
                and child.reference_type == HAS_PROPERTY_REFERENCE
            ):
                self.properties_to_read.append(child)

        # append read requests
        for propertyNode in self.properties_to_read:
            req.read_requests.append(
                ua.ReadValueId(
                    NodeId=propertyNode.node_id,
                    AttributeId=ua.attribute_ids.AttributeIds.Value,
                )
            )

        self._init_step += 1
        return req

    def _advance_step_1(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        if last_result is None:
            raise ValueError(
                f"Received Unexpected None Result for step {self._init_step}"
            )

        results = last_result.read_results
        attribute_count = len(ATTRIBUTES_TO_READ)

        # split result into attribute and property results and apply them to the node
        if len(results) != attribute_count + len(self.properties_to_read):
            raise ValueError(
                f"Expected {attribute_count + len(self.properties_to_read)} read results, got {len(results)}"
            )

        def is_usable(r: ua.DataValue) -> bool:
            return r.StatusCode is not None and not r.StatusCode.is_bad()

        self.opc_node.attributes = {
            attr.name: (r.Value.Value if r.Value is not None else None)
            for attr, r in zip(
                ATTRIBUTES_TO_READ,
                results[:attribute_count],
                strict=True,
            )
            if is_usable(r)
        }

        self.opc_node.properties = {
            node.browse_name.Name: r.Value
            for node, r in zip(
                self.properties_to_read,
                results[attribute_count:],
                strict=True,
            )
            if is_usable(r)
        }

        # done!
        self.entity = VariableEntity(opc_node=self.opc_node)
        self.init_state = FeatureInitState.DONE

        return None

    def request_subscription(
        self, event_bus: EventBus
    ) -> FeatureSubscribeRequest | None:
        req = FeatureSubscribeRequest(subscriptions=[])

        req.subscriptions.append(
            FeatureSubscribeDataRequest(
                attr=ua.attribute_ids.AttributeIds.Value,
                handler=self.on_value_update,
                node_id=self.opc_node.node_id,
            )
        )

        self.event_bus = event_bus

        return req

    def request_value(self) -> FeatureValueReadRequest | None:
        req = FeatureValueReadRequest(read_requests=[], feature=self)

        req.read_requests.append(
            ua.ReadValueId(
                NodeId=self.opc_node.node_id,
                AttributeId=ua.attribute_ids.AttributeIds.Value,
            )
        )

        return req

    def handle_value_result(self, result: FeatureValueReadResult) -> None:
        if len(result.read_results) != 1:
            return

        first_result = result.read_results[0]

        if first_result.StatusCode is None or first_result.StatusCode.is_bad():
            return

        val_attr = self.opc_node.attributes.get("Value", None)

        if val_attr is None:
            return

        if first_result.Value is None:
            return

        self.opc_node.attributes["Value"] = first_result.Value.Value

    def on_value_update(self, node: Node, evt: DataChangeEvent):
        if not isinstance(self.entity, VariableEntity):
            return

        try:
            value = normalize_to_variant(evt.data.monitored_item.Value)

            if not isinstance(value, ua.Variant) or value is None:
                logger.warning(
                    "received unexpected None value update on VariableFeature"
                )
                return

            self.opc_node.attributes["Value"] = value

            data = VariantData.from_ua(value)
            self.entity.update_value(data)

            if self.event_bus is not None:
                self.event_bus.publish(
                    VariableValueUpdate(
                        entity_id=self.entity_id,
                        new_value=data,
                    )
                )

        except VariantNormalizationFailedError:
            logger.exception("Failed to handle update on VariableFeature")
