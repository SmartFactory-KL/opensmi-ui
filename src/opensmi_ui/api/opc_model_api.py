from fastapi import APIRouter, HTTPException
from starlette import status

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.browse import OPCModel
from opensmi_ui.opc_session.session import OPCSessionNotReadyError

logger = get_module_logger("opc_model_api")


def create_opc_model_api(opc_model: OPCModel) -> APIRouter:
    router = APIRouter(prefix="/api/opc-model", tags=["opc-model"])

    @router.get("/browse", summary="Request to (re-)browse the server")
    async def request_browse():
        try:
            await opc_model.browse()
        except OPCSessionNotReadyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Not ready to browse. Make sure a session is connected and ready",
            )
        except Exception:
            raise

    return router
