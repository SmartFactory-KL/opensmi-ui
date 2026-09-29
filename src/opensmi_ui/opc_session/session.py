from dataclasses import dataclass

from asyncua.client.client import Client

from opensmi_ui.logger import get_module_logger

logger = get_module_logger("opc_session")


@dataclass(frozen=True)
class OPCSessionSettings:
    timeout: float = 30.0
    auto_reconnect: bool = True

    reconnect_max_delay: float = 60.0
    watchdog_intervall: float = 5.0

    reconnect_request_timeout: float = 60.0


class OPCSession:
    _opc_client: Client

    def __init__(
        self,
        url: str,
        settings: OPCSessionSettings | None = None,
    ):
        if settings is None:
            settings = OPCSessionSettings()

        self._opc_client = Client(
            url=url,
            timeout=settings.timeout,
            auto_reconnect=settings.auto_reconnect,
            reconnect_max_delay=settings.reconnect_max_delay,
            reconnect_request_timeout=settings.reconnect_request_timeout,
            watchdog_intervall=settings.watchdog_intervall,
        )

        self._opc_client.application_uri = ""
        self._opc_client.product_uri = "urn:smartfacotry-kl:opensmi_ui:session"

    def connect(self) -> bool:
        return False

    def disconnect(self) -> bool:
        return False
