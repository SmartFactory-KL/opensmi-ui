from typing import Any
from uuid import UUID

from asyncua import ua
from asyncua.common.node import Node
from asyncua.common.subscription import DataChangeEvent

from opensmi_ui.event.bus import EventBus
from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.json import JsonOutModel
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


class VariableFeatureNode(FeatureNode):
    _init_step: int

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self._init_step = 0
        self.entity_type = "Variable"

    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        match self._init_step:
            case 0:
                self.init_state = FeatureInitState.PENDING

                # first step is to read the attributes and browse properties that are available
                req = FeatureInitRequest(
                    browse_requests=[], read_requests=[], feature=self
                )

                for attr in ATTRIBUTES_TO_READ:
                    req.read_requests.append(
                        ua.ReadValueId(NodeId=self.opc_node.node_id, AttributeId=attr)
                    )

                # TODO: These nodes are actually already available
                # TODO: within opc_node.children -> Decide how to handle that?
                req.browse_requests.append(
                    ua.BrowseDescription(
                        NodeId=self.opc_node.node_id,
                        BrowseDirection=ua.BrowseDirection.Forward,
                        ReferenceTypeId=ua.NodeId(
                            ua.Int32(ua.object_ids.ObjectIds.HasProperty)
                        ),
                        IncludeSubtypes=True,
                        NodeClassMask=ua.NodeClass.Variable,
                        ResultMask=ua.BrowseResultMask.All,
                    )
                )

                self._init_step += 1
                return req
            case 1:
                if last_result is None:
                    self.init_state = FeatureInitState.ERROR
                    self.init_error = (
                        f"Received Unexpected None Result for step {self._init_step}"
                    )
                    return None

                # attach attributes to node
                available_attributes = {}
                for attr_idx, attr in enumerate(last_result.read_results):
                    if attr.StatusCode is None or attr.StatusCode.is_bad():
                        continue

                    available_attributes[ATTRIBUTES_TO_READ[attr_idx].name] = (
                        attr.Value.Value if attr.Value is not None else None
                    )

                self.opc_node.attributes = available_attributes

                # handle additional variable properties
                available_properties = {}
                for browses in last_result.browse_results:
                    for ref in browses.References:
                        available_properties[ref.BrowseName.Name] = ref
                self.opc_node.properties = available_properties

                # if no properties are available, we are done.
                # Otherwise their values need to be read
                if len(available_properties) == 0:
                    self.entity = VariableEntity(opc_node=self.opc_node)
                    self.init_state = FeatureInitState.DONE

                    return None
                else:
                    req = FeatureInitRequest(
                        read_requests=[], browse_requests=[], feature=self
                    )
                    for ref in self.opc_node.properties.values():
                        req.read_requests.append(
                            ua.ReadValueId(
                                NodeId=ref.NodeId,
                                AttributeId=ua.attribute_ids.AttributeIds.Value,
                            )
                        )

                    self._init_step += 1
                    return req

            case 2:
                if last_result is None:
                    self.init_state = FeatureInitState.ERROR
                    self.init_error = (
                        f"Received Unexpected None Result for step {self._init_step}"
                    )
                    return None

                props_with_values = {}

                for idx, key in enumerate(self.opc_node.properties.keys()):
                    cur_result = last_result.read_results[idx]

                    if cur_result.StatusCode is None or cur_result.StatusCode.is_bad():
                        continue

                    props_with_values[key] = last_result.read_results[idx].Value

                self.opc_node.properties = props_with_values

                self.entity = VariableEntity(opc_node=self.opc_node)

                self._init_step += 1
                self.init_state = FeatureInitState.DONE
                return None
            case _:
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
