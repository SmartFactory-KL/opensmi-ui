from fastapi import APIRouter, HTTPException
from starlette import status

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.browser import OPCBrowser
from opensmi_ui.opc_model.model_node import ComponentNodeData
from opensmi_ui.opc_session.session import OPCSessionNotReadyError

logger = get_module_logger("opc_model_api")


def create_opc_model_api(opc_model: OPCBrowser) -> APIRouter:
    router = APIRouter(prefix="/api/opc-model", tags=["opc-model"])

    @router.get("/browse", summary="Request to (re-)browse the server")
    async def request_browse() -> list[ComponentNodeData]:
        try:
            component_trees = await opc_model.read_model()
            return component_trees
        except OPCSessionNotReadyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Not ready to browse. Make sure a session is connected and ready",
            )
        except Exception:
            raise

    return router
