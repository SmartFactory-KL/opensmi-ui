from fastapi import APIRouter, HTTPException, Response
from starlette import status

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_client.client import (
    OPCClient,
    OPCClientConnectRequest,
    OPCClientSessionNotReadyError,
)

logger = get_module_logger("opc_session_api")


def create_opc_client_api(opc_client: OPCClient) -> APIRouter:
    router = APIRouter(prefix="/api/opc-session", tags=["opc-session"])

    @router.get("/info", summary="Get Session Data")
    async def get_info():
        info = opc_client.get_session_data()
        return info

    @router.post("/connect", summary="Connect to a server")
    async def post_connect(request: OPCClientConnectRequest):
        logger.info(request)

        try:
            await opc_client.connect(
                OPCClientConnectRequest(
                    url=request.url,
                    username=request.username,
                    password=request.password,
                )
            )
        except OPCClientSessionNotReadyError as e:
            raise HTTPException(detail=str(e), status_code=status.HTTP_409_CONFLICT)
        except ConnectionError as e:
            raise HTTPException(
                detail=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post("/disconnect", summary="Disconnect from a server")
    async def post_disconnect():
        await opc_client.disconnect()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.get("/model", summary="Get the currently browsed model")
    async def get_model():
        machines = opc_client.get_machines()
        return machines

    return router
