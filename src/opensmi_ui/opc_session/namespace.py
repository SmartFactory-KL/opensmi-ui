from dataclasses import dataclass
from enum import StrEnum

from asyncua import ua

from opensmi_ui.logger import get_module_logger

logger = get_module_logger("opc_session.namespace")


class NamespaceNotReadyError(RuntimeError):
    """Raised whenever the namespace is called but not ready to use"""


class NamespaceNotFoundError(LookupError):
    """Raised whenever an entry within the namespace was not found"""


@dataclass(frozen=True)
class UriNodeId:
    Identifier: ua.Int32 | ua.String | ua.Guid | ua.ByteString
    NamespaceUri: str


class DefaultNamespaceURI(StrEnum):
    # --- Always present ---
    # Index 0 is fixed by the spec and always has this URI.
    # (The previous value "" was wrong; the URI is not empty.)
    OPC_UA_0 = "http://opcfoundation.org/UA/"

    # --- Common OPC Foundation companion specifications ---
    DI = "http://opcfoundation.org/UA/DI/"  # Devices (Part 100)
    IA = "http://opcfoundation.org/UA/IA/"  # Industrial Automation
    MACHINERY = "http://opcfoundation.org/UA/Machinery/"
    MACHINERY_JOBS = "http://opcfoundation.org/UA/Machinery/Jobs/"
    MACHINERY_RESULT = "http://opcfoundation.org/UA/Machinery/Result/"
    MACHINE_TOOL = "http://opcfoundation.org/UA/MachineTool/"
    PACKML = "http://opcfoundation.org/UA/PackML/"
    ADI = "http://opcfoundation.org/UA/ADI/"  # Analyzer Devices
    AUTO_ID = "http://opcfoundation.org/UA/AutoID/"
    ROBOTICS = "http://opcfoundation.org/UA/Robotics/"
    MACHINE_VISION = "http://opcfoundation.org/UA/MachineVision"  # no trailing slash
    PUMPS = "http://opcfoundation.org/UA/Pumps/"
    WOODWORKING = "http://opcfoundation.org/UA/Woodworking/"
    EUROMAP_77 = "http://opcfoundation.org/UA/EUROMAP77/"
    EUROMAP_83 = "http://opcfoundation.org/UA/EUROMAP83/"
    ISA95_JOB_CONTROL = "http://opcfoundation.org/UA/ISA95-JOBCONTROL_V2/"
    GDS = "http://opcfoundation.org/UA/GDS/"  # Global Discovery Server
    PLCOPEN = "http://PLCopen.org/OpcUa/IEC61131-3/"

    # --- Other ---
    # asyncua's default application URI, which ends up at index 1 unless you
    # call server.set_application_uri(). Index 1 is server-specific by spec.
    ASYNCUA_SERVER = "urn:freeopcua:python:server"

    # Project-specific
    SFKL_MACHINE = "http://smartfactory.de/UA/MachineSet"


class OPCNamespace:
    def __init__(self):

        self._is_ready: bool = False

        self._namespaces: list[str] = []
        self._ns_uri_idx: dict[str, int] = {}

        self._cache: dict[UriNodeId, ua.NodeId] = {}

        self.reset()

    def reset(self) -> None:
        self._is_ready = False

        self._namespaces = []
        self._ns_uri_idx = {}

        self._cache = {}

    def is_ready(self) -> bool:
        return self._is_ready

    def update_namespaces(self, namespaces: list[str]) -> None:
        self.reset()

        ns_uri_idx: dict[str, int] = {}

        for idx, _ns in enumerate(namespaces):
            if _ns in ns_uri_idx:
                logger.warning(f"Found Duplicate Namespace! {_ns} appears twice.")

            ns_uri_idx[_ns] = idx

        self._ns_uri_idx = ns_uri_idx
        self._namespaces = namespaces

        self._is_ready = True

    def _require_ready(self):
        if not self._is_ready:
            raise NamespaceNotReadyError("Namespace is not ready")

    def uri_to_idx(self, uri: str) -> ua.Int16:
        self._require_ready()

        idx = self._ns_uri_idx.get(uri, None)
        if idx is None:
            raise NamespaceNotFoundError(f"Cannot find NamespaceIndex for {uri}")

        return ua.Int16(idx)

    def idx_to_uri(self, idx: int) -> str:
        self._require_ready()

        if idx < 0 or idx >= len(self._namespaces):
            raise NamespaceNotFoundError(f"Cannot find URI for NamespaceIndex {idx}")

        uri = self._namespaces[idx]

        return uri

    def to_node_id(self, uri_node_id: UriNodeId) -> ua.NodeId:
        self._require_ready()

        if uri_node_id in self._cache:
            return self._cache[uri_node_id]

        idx = self.uri_to_idx(uri_node_id.NamespaceUri)

        node_id = ua.NodeId(
            Identifier=uri_node_id.Identifier,
            NamespaceIndex=idx,
        )

        self._cache[uri_node_id] = node_id

        return node_id

    def to_uri_node_id(self, node_id: ua.NodeId) -> UriNodeId:
        self._require_ready()

        uri = self.idx_to_uri(node_id.NamespaceIndex)

        return UriNodeId(
            Identifier=node_id.Identifier,
            NamespaceUri=uri,
        )
