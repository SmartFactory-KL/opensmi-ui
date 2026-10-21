from abc import abstractmethod

from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.opc_node import OPCNode


class FeatureNodeEntityData(JsonOutModel): ...


class FeatureNodeEntity:
    @abstractmethod
    def __init__(self, opc_node: OPCNode):
        ...

    @abstractmethod
    def get_data(self) -> FeatureNodeEntityData:
        return FeatureNodeEntityData()
