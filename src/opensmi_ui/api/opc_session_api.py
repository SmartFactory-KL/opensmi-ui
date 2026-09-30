from fastapi import APIRouter, Response

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.common import JsonBaseModel
from opensmi_ui.opc_session.session import OPCSession

logger = get_module_logger("opc_session_api")


class OPCSessionConnectRequest(JsonBaseModel):
    url: str = ""
    username: str = ""
    password: str = ""


def create_opc_session_api(opc_session: OPCSession) -> APIRouter:
    router = APIRouter(prefix="/api/opc-session", tags=["opc-session"])

    @router.get("/info", summary="Get Session Data")
    async def get_info():
        info = opc_session.get_info()
        return info

    @router.post("/connect", summary="Connect to a server")
    async def post_connect(request: OPCSessionConnectRequest, response: Response):
        pass

    @router.post("/disconnect", summary="Disconnect from a server")
    async def post_disconnect(response: Response):
        pass

    return router
