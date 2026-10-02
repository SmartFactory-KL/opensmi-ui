from opensmi_ui.opc_model.mif_factory import MIF
from opensmi_ui.opc_model.node import OPCNode


# MIF = MachineryItemFeature
class MIFContainer:
    def __init__(self, opc_node: OPCNode):
        self.opc_node = opc_node

    def create_with_features(self, features: list[MIF]):
        pass
