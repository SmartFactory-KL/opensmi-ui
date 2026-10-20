from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.features.machinery_item_state_feature import ua
from opensmi_ui.opc_model.opc_node import NodeIdData, OPCNode


class DependencyEntityData(FeatureNodeEntityData):
    name: str

    depends_on: list[NodeIdData]
    dependeny_of: list[NodeIdData]


class DependencyEntity(FeatureNodeEntity):
    content: DependencyEntityData

    def __init__(
        self,
        opc_node: OPCNode,
        depends_on: list[ua.NodeId],
        dependency_of: list[ua.NodeId],
    ):

        self.content = DependencyEntityData(
            name=opc_node.browse_name.Name,
            dependeny_of=[NodeIdData.from_ua(dep) for dep in dependency_of],
            depends_on=[NodeIdData.from_ua(dep) for dep in depends_on],
        )

    def get_data(self) -> DependencyEntityData:
        return self.content
