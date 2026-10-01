from collections import deque

from asyncua import ua
from asyncua.ua.attribute_ids import AttributeIds

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.node import create_opc_node
from opensmi_ui.opc_session.session import OPCSession, OPCSessionNotReadyError

logger = get_module_logger("opc_model")


class OPCModel:
    def __init__(self, opc_session: OPCSession):
        self.opc_session = opc_session

    async def browse(self):
        if not self.opc_session.is_ready():
            raise OPCSessionNotReadyError(
                f"failed to browse: opc session not ready, state {self.opc_session.opc_client.state}"
            )

        logger.info("Browsing nodes..")

        root_node_id = ua.NodeId(
            Identifier=ua.Int32(1001),
            NamespaceIndex=self.opc_session.namespace_idx(
                "http://opcfoundation.org/UA/Machinery/"
            ),
        )

        nodes_to_process = deque([root_node_id])
        visited: set[ua.NodeId] = set()

        while nodes_to_process:
            next_node_id = nodes_to_process.popleft()
            if next_node_id in visited:
                continue
            visited.add(next_node_id)

            opc_node = await create_opc_node(self.opc_session, next_node_id)
            print(opc_node)

            children = await opc_node.ua_node().get_children()

            for child in children:
                if child.nodeid not in visited:
                    nodes_to_process.append(child.nodeid)
