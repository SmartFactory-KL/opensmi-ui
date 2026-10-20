from opensmi.client.remote_variable import ua

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.user_entity import UserEntity
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureInitState,
    FeatureNode,
)
from opensmi_ui.opc_model.opc_node import OPCNode

logger = get_module_logger("opc_model.features.user")


class UserFeatureNode(FeatureNode):
    _init_step: int

    def __init__(
        self,
        opc_node: OPCNode,
        parent_component_node: ComponentNode,
        parent_feature_node: FeatureNode | None = None,
    ):
        super().__init__(opc_node, parent_component_node, parent_feature_node)
        self._init_step = 0
        self.entity_type = "User"

    def advance(
        self, last_result: FeatureInitResult | None
    ) -> FeatureInitRequest | None:
        match self._init_step:
            case 0:
                self.init_state = FeatureInitState.PENDING

                req = FeatureInitRequest(
                    browse_requests=[], read_requests=[], feature=self
                )

                for child in self.opc_node.children:
                    req.read_requests.append(
                        ua.ReadValueId(
                            NodeId=child.node_id,
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

                for idx, child in enumerate(self.opc_node.children):
                    match child.browse_name.Name:
                        case (
                            "AllowMultiple"
                            | "UserLevel"
                            | "MaxAccessLevel"
                            | "IsPresent"
                        ):
                            cur_result = last_result.read_results[idx]

                            if (
                                cur_result.StatusCode is None
                                or cur_result.StatusCode.is_bad()
                            ):
                                continue

                            child.attributes["Value"] = cur_result.Value

                self.entity = UserEntity(opc_node=self.opc_node)

                self._init_step += 1
                self.init_state = FeatureInitState.DONE

                return None
            case _:
                return None
