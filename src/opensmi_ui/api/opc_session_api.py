from asyncua.ua.uaerrors import BadUserAccessDenied
from fastapi import APIRouter, HTTPException, Response
from starlette import status

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.common import JsonBaseModel
from opensmi_ui.opc_session.session import OPCSession, OPCSessionAlreadyConnectedError

logger = get_module_logger("opc_session_api")


class OPCSessionConnectRequest(JsonBaseModel):
    url: str = ""
    username: str = ""
    password: str = ""


def create_opc_session_api(opc_session: OPCSession) -> APIRouter:
    router = APIRouter(prefix="/api/opc-session", tags=["opc-session"])

    @router.get("/info", summary="Get Session Data")
    async def get_info():
        info = opc_session.get_session_data()
        return info

    @router.post("/connect", summary="Connect to a server")
    async def post_connect(request: OPCSessionConnectRequest):
        logger.info(request)
        try:
            await opc_session.connect(request.url, request.username, request.password)
        except ConnectionRefusedError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Got ConnectionRefused, please make sure the URL {request.url!r} is correct and the server is running",
            )
        except OPCSessionAlreadyConnectedError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Connection already established, please disconnect first",
            )
        except BadUserAccessDenied:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access Denied. Please check username and password.",
            )
        except Exception:
            raise

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post("/disconnect", summary="Disconnect from a server")
    async def post_disconnect():
        await opc_session.disconnect()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
