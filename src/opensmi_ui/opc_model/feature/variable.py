from typing import Any

from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.node import OPCNode

logger = get_module_logger("opc_model.feature.variable")


class VariableNode:
    opc_node: OPCNode

    data_type: ua.NodeId
    value_rank: int
    array_dimensions: list[int] | None

    access_level: ua.AccessLevel
    user_access_level: ua.AccessLevel

    minimum_sampling_interval: float
    historizing: bool

    data_value: ua.DataValue | None = None
    value: Any

    children: list["VariableNode"]

    def __init__(self, opc_node: OPCNode):
        self.opc_node = opc_node
        self.children = []

    def write_value(self, value: Any):
        self.value = value

    def __str__(self) -> str:
        return (
            f"VariableNode: {self.opc_node.browse_name.Name}\n"
            f"  Node ID:                    {self.opc_node.node_id}\n"
            f"  Value:                      {self.value!r}\n"
            f"  Data type:                  {self.data_type}\n"
            f"  Value rank:                 {self.value_rank}\n"
            f"  Array dimensions:           {self.array_dimensions}\n"
            f"  Access level:               {self.access_level}\n"
            f"  User access level:          {self.user_access_level}\n"
            f"  Minimum sampling interval:  {self.minimum_sampling_interval}\n"
            f"  Historizing:                {self.historizing}"
        )
