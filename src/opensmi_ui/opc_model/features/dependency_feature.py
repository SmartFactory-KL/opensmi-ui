from asyncua import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.dependency_entity import DependencyEntity
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
    FeatureSubscribeRequest,
)
from opensmi_ui.opc_model.opc_node import OPCNode

logger = get_module_logger("opc_model.features.dependency")


class DependencyFeatureNode(FeatureNode):
    _init_step: int

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self._init_step = 0
        self.entity_type = "Dependency"

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

                # browse references
                req.browse_requests.append(
                    ua.BrowseDescription(
                        BrowseDirection=ua.BrowseDirection.Both,
                        IncludeSubtypes=True,
                        NodeClassMask=ua.NodeClass.Unspecified,
                        NodeId=self.opc_node.node_id,
                        ReferenceTypeId=ua.NodeId(
                            ua.Int32(ua.object_ids.ObjectIds.References)
                        ),
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

                depends_on = []
                dependency_of = []
                if len(last_result.browse_results) > 0:
                    dependency_result = last_result.browse_results[0]

                    if not dependency_result.StatusCode.is_bad():
                        for ref in dependency_result.References:
                            if not isinstance(ref, ua.ReferenceDescription):
                                continue

                            if ref.IsForward:
                                depends_on.append(ref.NodeId)
                            else:
                                dependency_of.append(ref.NodeId)

                self.entity = DependencyEntity(
                    opc_node=self.opc_node,
                    depends_on=depends_on,
                    dependency_of=dependency_of,
                )

                self._init_step += 1
                self.init_state = FeatureInitState.DONE
                return None

            case _:
                return None
