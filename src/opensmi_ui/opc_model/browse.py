from collections import deque
from time import perf_counter

from asyncua import ua
from asyncua.ua.uaprotocol_auto import ReferenceDescription

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.const import COMPONENTS_BROWSE_NAME, MACHINE_IDENTIFIER
from opensmi_ui.opc_model.mif_factory import add_containers_to_component_tree
from opensmi_ui.opc_model.model import (
    ComponentTree,
    ComponentTreeReadItem,
    NodeReadItem,
)
from opensmi_ui.opc_model.node import OPCNode
from opensmi_ui.opc_session.session import OPCSession, OPCSessionNotReadyError

logger = get_module_logger("opc_model.browse")


def print_component_trees(trees: list[ComponentTree]) -> None:
    """Print component trees in a human-readable tree format."""

    def print_tree(tree: ComponentTree, prefix: str = "", is_last: bool = True) -> None:
        name = tree.node.browse_name.Name
        child_count = len(tree.node.get_children())

        branch = "└── " if is_last else "├── "
        print(f"{prefix}{branch}{name}[{child_count}]")

        for feature in tree.node.get_children():
            print(f"{prefix}    +{feature.display_name.Text}")

        prefix += "    "

        for i, child in enumerate(tree.children):
            print_tree(
                child,
                prefix,
                is_last=(i == len(tree.children) - 1),
            )

    for i, tree in enumerate(trees):
        print_tree(
            tree,
            is_last=(i == len(trees) - 1),
        )


class OPCModel:
    def __init__(self, opc_session: OPCSession):
        self.opc_session = opc_session

    async def browse_basic_nodes(self) -> list[OPCNode]:
        """Reads the nodes and returns them as a list of node-trees while only reading basic information"""
        if not self.opc_session.is_connected():
            raise OPCSessionNotReadyError(
                f"failed to browse: opc session not ready, state {self.opc_session.opc_client.state}"
            )

        # TODO: This could emit notifications like "browse_start" and milestones
        logger.info("Browsing nodes..")

        # read machines node
        machines_node_id = ua.NodeId(
            Identifier=MACHINE_IDENTIFIER,
            NamespaceIndex=self.opc_session.namespace_idx(
                "http://opcfoundation.org/UA/Machinery/"
            ),
        )

        # add all children as "root components" to be browsed
        current_level = deque[NodeReadItem](
            [NodeReadItem(node_id=machines_node_id, parent_node=None)]
        )
        next_level = deque[NodeReadItem]([])

        # keep a set of visited nodes to prevent re-visiting
        visited: set[ua.NodeId] = set()

        # keep the list of top level nodes, which are "Machines"
        root_nodes: list[OPCNode] = []

        # go down level by level and aggregate all items of a single
        # level before requesting all of them at once
        while current_level or next_level:
            # browse next level
            # instead of using get_children() on all single nodes
            # this will batch one big read including all nodes on the current level
            # and return them all in one go
            browse_desc = [
                ua.BrowseDescription(
                    NodeId=item.node_id,
                    BrowseDirection=ua.BrowseDirection.Forward,
                    ReferenceTypeId=ua.NodeId(
                        ua.Int32(ua.object_ids.ObjectIds.HierarchicalReferences)
                    ),
                    IncludeSubtypes=True,
                    NodeClassMask=0,
                    ResultMask=ua.BrowseResultMask.All,
                )
                for item in current_level
            ]

            # convert to parameters - no idea why?
            params = ua.BrowseParameters(NodesToBrowse=browse_desc)

            # send the actual request
            results = await self.opc_session.opc_client.uaclient.browse(params)

            # handle the results: their order should be the order of current_level
            for result_idx, browse_result in enumerate(results):
                if not isinstance(browse_result, ua.BrowseResult):
                    raise TypeError(
                        f"expected browse result but got {type(browse_result)}"
                    )

                if browse_result.ContinuationPoint is not None:
                    # TODO: Handle the continuation!
                    logger.error("Continuation Point found!")

                for ref in browse_result.References:
                    # mostly for typing
                    if not isinstance(ref, ReferenceDescription):
                        continue

                    if ref.NodeId in visited:
                        continue

                    visited.add(ref.NodeId)

                    # get the ReadItem to know where to append the node to
                    node_read_item = current_level[result_idx]

                    # create the Node from the reference
                    opc_node = OPCNode(
                        node_id=ref.NodeId,
                        ua_node=self.opc_session.opc_client.get_node(ref.NodeId),
                        node_class=ref.NodeClass,
                        browse_name=ref.BrowseName,
                        display_name=ref.DisplayName,
                    )

                    # append the node to its parent
                    if node_read_item.parent_node is None:
                        root_nodes.append(opc_node)
                    else:
                        node_read_item.parent_node.append_child(opc_node=opc_node)

                    # also append it to the next level for browsing
                    next_level.append(
                        NodeReadItem(node_id=ref.NodeId, parent_node=opc_node)
                    )

            current_level = next_level
            next_level = deque[NodeReadItem]([])

        return root_nodes

    def get_component_trees(self, nodes: list[OPCNode]) -> list[ComponentTree]:
        """Take a list of OPCNodes and return a component tree with only the components"""
        trees: list[ComponentTree] = []

        for node in nodes:
            root_tree: ComponentTree | None = None

            nodes_to_read = deque([ComponentTreeReadItem(node=node, parent_tree=None)])
            while nodes_to_read:
                next_item = nodes_to_read.popleft()

                tree = ComponentTree(node=next_item.node, children=[])

                if next_item.parent_tree is None:
                    root_tree = tree
                else:
                    next_item.parent_tree.children.append(tree)

                for child in next_item.node.get_children():
                    if child.browse_name.Name == COMPONENTS_BROWSE_NAME:
                        for child_component in child.get_children():
                            nodes_to_read.append(
                                ComponentTreeReadItem(
                                    node=child_component, parent_tree=tree
                                )
                            )
            if root_tree is not None:
                trees.append(root_tree)

        return trees

    async def browse(self):
        # read basic nodes
        browse_start = perf_counter()
        basic_nodes = await self.browse_basic_nodes()
        basic_nodes_duration = perf_counter() - browse_start
        logger.info("Basic Node Browsing took %.6f seconds", basic_nodes_duration)

        # convert to basic components tree
        tree_convert_start = perf_counter()
        component_trees = self.get_component_trees(basic_nodes)
        print_component_trees(component_trees)
        tree_convert_duration = perf_counter() - tree_convert_start
        logger.info("Tree Conversion took %.6f seconds", tree_convert_duration)

        # use component tree to create MIFContainer
        container_create_start = perf_counter()
        container_trees: list[ComponentTree] = []
        for component_tree in component_trees:
            container_tree = add_containers_to_component_tree(component_tree)
            container_trees.append(container_tree)
        container_create_duration = perf_counter() - container_create_start
        logger.info("Container Creation took %.6f seconds", container_create_duration)

        # add subscriptions

        # read values
        value_read_start = perf_counter()
        components_to_process = deque[ComponentTree](container_trees)
        while components_to_process:
            next_item = components_to_process.popleft()

            if next_item.mifco is not None:
                for feature in next_item.mifco.features:
                    await feature.read_values(opc_session=self.opc_session)

            for child in next_item.children:
                components_to_process.append(child)

        value_read_duration = perf_counter() - value_read_start
        logger.info("Value Reading took %.6f seconds", value_read_duration)

        # done!
