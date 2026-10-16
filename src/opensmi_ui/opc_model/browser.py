from collections import deque
from dataclasses import dataclass
from time import perf_counter

from asyncua import ua
from asyncua.ua.uaprotocol_auto import ReferenceDescription

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.entities.component_entity import ComponentEntity
from opensmi_ui.opc_model.feature_proxy import (
    FeatureNotKnownError,
    FeatureSkippedError,
    create_features_for_node,
)
from opensmi_ui.opc_model.model_node import (
    ComponentNode,
    ComponentNodeData,
    FeatureInitRequest,
    FeatureInitResult,
    FeatureNode,
    visit_tree_features,
)
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_session.session import OPCSession, OPCSessionNotReadyError

logger = get_module_logger("opc_model.browse")

MACHINE_IDENTIFIER = ua.Int32(1001)
COMPONENTS_BROWSE_NAME = "Components"

BROWSE_CHUNK_SIZE = 200
"""This defines the chunk size for browsing nodes. If more then this amount of nodes would be browsed,
the browsing will be split into multiple requests."""

READ_CHUNK_SIZE = 200
"""This defines the chunk size for reading node attributes."""

MAX_FEATURE_ADVANCE_COUNT = 20
"""This is a boundary to check for 'infinite' loops within the feature advancing. No feature can have more than this amount of advance steps."""


@dataclass(frozen=True)
class OPCNodeReadItem:
    opc_node: OPCNode
    parent_component_node: ComponentNode | None


@dataclass(frozen=True)
class ComponentNodeReadItem:
    component_node: ComponentNode
    parent: ComponentNode | None


@dataclass(frozen=True)
class NodeReadItem:
    node_id: ua.NodeId
    parent_node: OPCNode | None


class OPCBrowser:
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

        # counts runs to show some sort of progress bar
        run_count = 0
        node_count = 0

        # go down level by level and aggregate all items of a single
        # level before requesting all of them at once
        while current_level or next_level:
            run_count += 1
            node_count += len(current_level)

            # browse next level
            # instead of using get_children() on all single nodes
            # this will batch one big read including all nodes on the current level
            # and return them all in one go
            browse_descriptions = [
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

            # send the actual request in batches of n to prevent running into operation limit
            results = await self._browse_all_in_chunks(
                browse_descriptions=browse_descriptions
            )

            # handle the results: their order should be the order of current_level
            for result_idx, browse_result in enumerate(results):
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
                        type_definition_id=ref.TypeDefinition,
                        reference_type_id=ref.ReferenceTypeId,
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

            # swap
            current_level = next_level
            next_level = deque[NodeReadItem]([])

        logger.info(f"Basic Node Reading found {node_count} Nodes")

        return root_nodes

    async def _read_all_in_chunks(
        self, reading_requests: list[ua.ReadValueId]
    ) -> list[ua.DataValue]:
        logger.info(f"Reading {len(reading_requests)} elements")

        read_chunks = [
            reading_requests[i : i + READ_CHUNK_SIZE]
            for i in range(0, len(reading_requests), READ_CHUNK_SIZE)
        ]

        results: list[ua.DataValue] = []

        for idx, chunk in enumerate(read_chunks):
            if len(read_chunks) > 1:
                logger.info(f"Reading Chunk {idx + 1} of {len(read_chunks)}")

            # convert to parameters - no idea why?
            params = ua.ReadParameters(
                NodesToRead=chunk,
            )
            chunk_results = await self.opc_session.opc_client.uaclient.read(params)

            if len(chunk_results) != len(chunk):
                raise ValueError(
                    f"The result contains {len(chunk_results)} elements instead of the expected {len(chunk)} elements. Something went wrong."
                )

            # Status Codes are not checked here, as that is done by the features themselves.
            results.extend(chunk_results)

        return results

    async def _browse_all_in_chunks(
        self, browse_descriptions: list[ua.BrowseDescription]
    ) -> list[ua.BrowseResult]:
        logger.info(f"Browsing {len(browse_descriptions)} elements")

        browse_chunks = [
            browse_descriptions[i : i + BROWSE_CHUNK_SIZE]
            for i in range(0, len(browse_descriptions), BROWSE_CHUNK_SIZE)
        ]

        results: list[ua.BrowseResult] = []

        for idx, chunk in enumerate(browse_chunks):
            if len(browse_chunks) > 1:
                logger.info(f"Browsing Chunk {idx + 1} of {len(browse_chunks)}")

            # convert to parameters - no idea why?
            params = ua.BrowseParameters(
                NodesToBrowse=chunk,
            )
            chunk_results = await self.opc_session.opc_client.uaclient.browse(params)

            if len(chunk_results) != len(chunk):
                raise ValueError(
                    f"The result contains {len(chunk_results)} elements instead of the expected {len(chunk)} elements. Something went wrong."
                )

            for chunk_result in chunk_results:
                if chunk_result.ContinuationPoint is None:
                    continue
                else:
                    logger.warning("ContinuationPoint!")
                    logger.warning(chunk_result.ContinuationPoint)
                    # TODO: Actually implement the ContinuationPoint
                    # HOWEVER: https://github.com/FreeOpcUa/opcua-asyncio/blob/master/asyncua/server/internal_session.py#L246
                    # This states that browse_next is not implemented on asyncua server - so I cannot reliably test it anyway now.

            results.extend(chunk_results)

        return results

    async def read_model(self) -> list[ComponentNodeData]:
        # read basic nodes
        browse_start = perf_counter()
        basic_nodes = await self.browse_basic_nodes()
        basic_nodes_duration = perf_counter() - browse_start
        logger.info("Basic Node Reading took %.6f seconds", basic_nodes_duration)

        # convert to basic components tree
        tree_convert_start = perf_counter()
        component_trees = get_component_trees(basic_nodes)
        tree_convert_duration = perf_counter() - tree_convert_start
        logger.info("Tree Conversion took %.6f seconds", tree_convert_duration)

        # print_component_trees(component_trees)

        # create features for nodes
        feature_create_start = perf_counter()
        create_features_on_trees(component_trees)
        feature_create_duration = perf_counter() - feature_create_start
        logger.info("Feature Creation took %.6f seconds", feature_create_duration)

        # enrich features with entities using attributes and properties in
        # a recursive procedure
        feature_init_start = perf_counter()

        init_requests: list[FeatureInitRequest] = []

        def read_req(feature: FeatureNode, _) -> None:
            req = feature.advance(None)
            if req is not None:
                init_requests.append(req)

        for component_tree in component_trees:
            visit_tree_features(tree=component_tree, method=read_req)

        loop_count = 0
        while len(init_requests) > 0 and loop_count < MAX_FEATURE_ADVANCE_COUNT:
            loop_count += 1

            # create results list and next init
            next_init_requests: list[FeatureInitRequest] = []
            init_results: list[FeatureInitResult] = [
                FeatureInitResult(read_results=[], browse_results=[])
                for _ in init_requests
            ]

            # handle the reads and match them to their request
            reading_requests = aggregate_reading_requests(init_requests)
            reading_results = await self._read_all_in_chunks(
                reading_requests=reading_requests
            )
            result_idx = 0
            for req_idx, req in enumerate(init_requests):
                req_size = len(req.read_requests)

                results = reading_results[result_idx : (result_idx + req_size)]

                if req_size != len(results):
                    raise ValueError(
                        f"Size Mismatch on reading_results, got {len(results)} but expected {req_size}"
                    )

                init_results[req_idx].read_results = results
                result_idx += req_size

            # handle the browses and match them to their request
            browsing_requests = aggregate_browsing_requests(init_requests)
            browsing_results = await self._browse_all_in_chunks(
                browse_descriptions=browsing_requests
            )
            result_idx = 0
            for req_idx, req in enumerate(init_requests):
                req_size = len(req.browse_requests)

                results = browsing_results[result_idx : (result_idx + req_size)]

                if req_size != len(results):
                    logger.error(
                        f"Size Mismatch on browsing_results, got {len(results)} but expected {req_size}"
                    )

                init_results[req_idx].browse_results = results
                result_idx += req_size

            # advance all features using their results
            for idx, item in enumerate(init_requests):
                next_req = item.feature.advance(last_result=init_results[idx])

                if next_req is not None:
                    next_init_requests.append(next_req)

            init_requests = next_init_requests

        if loop_count >= MAX_FEATURE_ADVANCE_COUNT:
            raise RuntimeError(
                f"Feature Advancing resulted in loop count of over {MAX_FEATURE_ADVANCE_COUNT} - indicating an infinite loop. Check your feature advances."
            )

        feature_init_duration = perf_counter() - feature_init_start
        logger.info("Feature Initialization took %.6f seconds", feature_init_duration)

        # create subscriptions

        # read values

        # convert to serializables
        component_tree_data_list: list[ComponentNodeData] = []
        for component_tree in component_trees:
            component_tree_data_list.append(component_tree.get_data())

        return component_tree_data_list


def get_component_trees(nodes: list[OPCNode]) -> list[ComponentNode]:
    """Take a list of OPCNodes and return a component tree with only the components"""
    trees: list[ComponentNode] = []

    for node in nodes:
        root_component_node: ComponentNode | None = None

        nodes_to_read = deque(
            [OPCNodeReadItem(opc_node=node, parent_component_node=None)]
        )
        while nodes_to_read:
            next_item = nodes_to_read.popleft()

            component_node = ComponentNode(
                opc_node=next_item.opc_node,
                parent_component_node=next_item.parent_component_node,
            )

            component_node.entity = ComponentEntity(opc_node=next_item.opc_node)

            if next_item.parent_component_node is None:
                root_component_node = component_node
            else:
                next_item.parent_component_node.children.append(component_node)

            for child in next_item.opc_node.get_children():
                # only continue with child components, ignore other features for now
                if child.browse_name.Name == COMPONENTS_BROWSE_NAME:
                    # Two steps down: MyComponent1.Components.[ListOfChildComponents]
                    for child_component in child.get_children():
                        nodes_to_read.append(
                            OPCNodeReadItem(
                                opc_node=child_component,
                                parent_component_node=component_node,
                            )
                        )
        if root_component_node is not None:
            trees.append(root_component_node)

    return trees


def create_features_on_trees(component_trees: list[ComponentNode]):
    components_to_process = deque(component_trees)
    while components_to_process:
        next_component_node = components_to_process.popleft()

        for child_node in next_component_node.opc_node.children:
            try:
                new_features = create_features_for_node(
                    opc_node=child_node, parent_component_node=next_component_node
                )

                next_component_node.features.extend(new_features)
            except FeatureSkippedError:
                # mostly happens when the Components node is encountered and can be ignored
                continue
            except FeatureNotKnownError:
                # logger.warning(f"Encountered unknown BrowseName: {e}")
                continue

        for child in next_component_node.children:
            components_to_process.append(child)


def aggregate_reading_requests(input: list[FeatureInitRequest]) -> list[ua.ReadValueId]:
    result = []

    for req in input:
        result.extend(req.read_requests)

    return result


def aggregate_browsing_requests(
    input: list[FeatureInitRequest],
) -> list[ua.BrowseDescription]:
    result = []

    for req in input:
        result.extend(req.browse_requests)

    return result
