from fastapi import APIRouter

from opensmi_ui.logger import get_module_logger
from opensmi_ui.opc_model.model import OPCModel

logger = get_module_logger("opc_model_api")


def create_opc_model_api(opc_model: OPCModel) -> APIRouter:
    router = APIRouter(prefix="/api/opc-model", tags=["opc-model"])

    @router.get("/browse", summary="Request to (re-)browse the server")
    async def request_browse():
        await opc_model.browse()

    return router
