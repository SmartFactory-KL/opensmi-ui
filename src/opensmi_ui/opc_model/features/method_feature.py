from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.method_entity import MethodEntity
from opensmi_ui.opc_model.features.dependency_feature import DependencyFeatureNode
from opensmi_ui.opc_model.features.variable_container_feature import (
    VariableContainerFeatureNode,
)
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
    FeatureSubscribeRequest,
)
from opensmi_ui.opc_model.opc_node import OPCNode

logger = get_module_logger("opc_model.features.method")


class MethodFeatureNode(FeatureNode):
    _init_step: int

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self._init_step = 0
        self.entity_type = "Method"

        # create features
        for child in opc_node.children:
            match child.browse_name.Name:
                case "Monitoring":
                    self.features.append(
                        VariableContainerFeatureNode(
                            opc_node=child,
                            parent_component_node=parent_component_node,
                            parent_feature_node=self,
                        )
                    )
                case "ParameterSet":
                    self.features.append(
                        VariableContainerFeatureNode(
                            opc_node=child,
                            parent_component_node=parent_component_node,
                            parent_feature_node=self,
                        )
                    )
                case "FinalResultData":
                    self.features.append(
                        VariableContainerFeatureNode(
                            opc_node=child,
                            parent_component_node=parent_component_node,
                            parent_feature_node=self,
                        )
                    )
                case "Requirements":
                    self.features.append(
                        DependencyFeatureNode(
                            opc_node=child,
                            parent_component_node=parent_component_node,
                            parent_feature_node=self
                        )
                    )

    def subscribe(self) -> FeatureSubscribeRequest | None:
        return None

    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        match self._init_step:
            case 0:
                self.init_state = FeatureInitState.PENDING

                req = FeatureInitRequest(
                    browse_requests=[], read_requests=[], feature=self
                )

                min_access_level_node: OPCNode | None = None
                for child in self.opc_node.children:
                    if child.browse_name.Name == "MinAccessLevel":
                        min_access_level_node = child

                if min_access_level_node is not None:
                    req.read_requests.append(
                        ua.ReadValueId(
                            NodeId=min_access_level_node.node_id,
                            AttributeId=ua.attribute_ids.AttributeIds.Value,
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

                for child in self.opc_node.children:
                    if child.browse_name.Name == "MinAccessLevel":
                        val = last_result.read_results[0]

                        if val.StatusCode is None or val.StatusCode.is_bad():
                            continue

                        child.attributes["Value"] = val.Value

                self.entity = MethodEntity(opc_node=self.opc_node)

                self._init_step += 1
                self.init_state = FeatureInitState.DONE
                return None

            case _:
                return None
