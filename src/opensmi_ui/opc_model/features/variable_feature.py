from enum import StrEnum

from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.variable_entity import VariableEntity
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureNode,
    FeatureSubscribeRequest,
)
from opensmi_ui.opc_model.opc_node import OPCNode

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


class VariableInitState(StrEnum):
    OPEN = "open"
    RECEIVE_ATTRIBUTES_AND_BROWSE_PROPERTIES = "reveice_attributes_and_properties"
    RECEIVE_PROPERTIES_VALUE = "receive_properties_value"
    DONE = "done"
    ERROR = "error"


class VariableFeatureNode(FeatureNode):
    _init_state: VariableInitState

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self.entity_type = "Variable"
        self._init_state = VariableInitState.OPEN

    def subscribe(self) -> FeatureSubscribeRequest | None:
        return None

    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        match self._init_state:
            case VariableInitState.OPEN:
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

                self._init_state = (
                    VariableInitState.RECEIVE_ATTRIBUTES_AND_BROWSE_PROPERTIES
                )
                return req
            case VariableInitState.RECEIVE_ATTRIBUTES_AND_BROWSE_PROPERTIES:
                if last_result is None:
                    logger.warning(
                        "Feature received unintended None Result. Going into Error mode."
                    )
                    self._init_state = VariableInitState.ERROR
                    # TODO Think about wether this should stop the whole deal
                    # TODO or if the Feature will need some kind of error feedback property
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
                    self._init_state = VariableInitState.DONE
                    self.entity = VariableEntity(opc_node=self.opc_node)

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

                    self._init_state = VariableInitState.RECEIVE_PROPERTIES_VALUE
                    return req

            case VariableInitState.RECEIVE_PROPERTIES_VALUE:
                if last_result is None:
                    logger.warning(
                        "Feature received unintended None Result. Going into Error mode."
                    )
                    self._init_state = VariableInitState.ERROR
                    # TODO Think about wether this should stop the whole deal
                    # TODO or if the Feature will need some kind of error feedback property
                    return None

                props_with_values = {}

                for idx, key in enumerate(self.opc_node.properties.keys()):
                    cur_result = last_result.read_results[idx]

                    if cur_result.StatusCode is None or cur_result.StatusCode.is_bad():
                        continue

                    props_with_values[key] = last_result.read_results[idx].Value

                self.opc_node.properties = props_with_values

                self.entity = VariableEntity(opc_node=self.opc_node)

                return None

            case VariableInitState.ERROR:
                return None
            case _:
                return None
