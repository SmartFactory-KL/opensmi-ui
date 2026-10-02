from collections.abc import Mapping

from asyncua import ua
from asyncua.ua import DataValue, NodeClass, Variant
from asyncua.ua.attribute_ids import AttributeIds

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.feature.variable import VariableNode
from opensmi_ui.opc_model.model import MIFeature
from opensmi_ui.opc_model.node import OPCNode
from opensmi_ui.opc_session.session import OPCSession

logger = get_module_logger("opc_model.feature.identification")

_VARIABLE_ATTRIBUTES: list[AttributeIds] = [
    ua.attribute_ids.AttributeIds.Value,
    ua.attribute_ids.AttributeIds.DataType,
    ua.attribute_ids.AttributeIds.ValueRank,
    ua.attribute_ids.AttributeIds.ArrayDimensions,
    ua.attribute_ids.AttributeIds.AccessLevel,
    ua.attribute_ids.AttributeIds.UserAccessLevel,
    ua.attribute_ids.AttributeIds.MinimumSamplingInterval,
    ua.attribute_ids.AttributeIds.Historizing,
]


class IdentificationFeature(MIFeature):
    opc_node: OPCNode

    var_nodes: Mapping[str, VariableNode]

    def __init__(self, opc_node: OPCNode):
        self.opc_node = opc_node
        self.var_nodes = {}

        for child in opc_node.get_children():
            if child.node_class == NodeClass.Variable:
                self.var_nodes[child.browse_name.Name] = VariableNode(opc_node=child)

    async def add_subscriptions(self) -> None: ...

    async def read_values(self, opc_session: OPCSession) -> None:
        if not self.var_nodes:
            return

        nodes_to_read = []
        for variable in self.var_nodes.values():
            for attribute in _VARIABLE_ATTRIBUTES:
                nodes_to_read.append(
                    ua.ReadValueId(
                        NodeId=variable.opc_node.node_id, AttributeId=attribute
                    )
                )

        params = ua.ReadParameters(
            NodesToRead=nodes_to_read, TimestampsToReturn=ua.TimestampsToReturn.Both
        )

        results = await opc_session.opc_client.uaclient.read(params)

        attributes_per_variable = len(_VARIABLE_ATTRIBUTES)

        for variable_index, variable in enumerate(self.var_nodes.values()):
            start = variable_index * attributes_per_variable
            end = start + attributes_per_variable

            variable_results = results[start:end]

            for (attribute_id), result in zip(
                _VARIABLE_ATTRIBUTES,
                variable_results,
                strict=True,
            ):
                if not isinstance(result, DataValue):
                    logger.warning(
                        "Skipped attribute %s of variable %s: "
                        "expected DataValue, got %s",
                        attribute_id,
                        variable.opc_node.browse_name.Name,
                        type(result),
                    )
                    continue

                if result.StatusCode is None or result.StatusCode.is_bad():
                    logger.warning(
                        "Failed to read attribute %s of variable %s: %s",
                        attribute_id,
                        variable.opc_node.browse_name.Name,
                        result.StatusCode,
                    )
                    continue

                if result.Value is None or not isinstance(result.Value, Variant):
                    logger.warning(
                        "Skipped value because value is None or not a Variant"
                    )
                    continue

                value = result.Value.Value

                match attribute_id:
                    case AttributeIds.Value:
                        variable.data_value = result
                        variable.write_value(value)

                    case AttributeIds.DataType:
                        variable.data_type = value

                    case AttributeIds.ValueRank:
                        variable.value_rank = value

                    case AttributeIds.ArrayDimensions:
                        variable.array_dimensions = value

                    case AttributeIds.AccessLevel:
                        variable.access_level = value

                    case AttributeIds.UserAccessLevel:
                        variable.user_access_level = value

                    case AttributeIds.MinimumSamplingInterval:
                        variable.minimum_sampling_interval = value

                    case AttributeIds.Historizing:
                        variable.historizing = value

    def get_dto(self) -> Mapping[str, object]:
        return self.var_nodes
