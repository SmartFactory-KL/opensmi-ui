from fastapi import APIRouter, HTTPException, Response
from starlette import status

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.action import GenericAction
from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.opc_model import OPCModel, OPCModelState
from opensmi_ui.opc_session.session import OPCSessionNotReadyError
from opensmi_ui.opc_subscriber.subscriber import OPCSubscriber

logger = get_module_logger("opc_model_api")


class CurrentModelState(JsonOutModel):
    state: OPCModelState


def create_opc_model_api(
    opc_model: OPCModel, opc_subscriber: OPCSubscriber
) -> APIRouter:
    router = APIRouter(prefix="/api/opc-model", tags=["opc-model"])

    @router.get(
        "/state",
        summary="Get the model state. This determines whether or not data is available",
    )
    async def request_state() -> CurrentModelState:
        result = CurrentModelState(state=opc_model.get_state())
        return result

    @router.get(
        "/", summary="Get the current model. Remember to browse first if this is empty."
    )
    async def request_data():
        result = opc_model.get_model()
        return result

    @router.get("/browse", summary="Request to (re-)browse the server")
    async def request_browse():
        try:
            await opc_model.read_all_model_information(opc_subscriber=opc_subscriber)
        except OPCSessionNotReadyError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Not ready to browse. Make sure a session is connected and ready. Error: {e!s}",
            )
        except Exception:
            raise

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post(
        "/action",
        summary="Request to use an action",
    )
    async def request_action(action: GenericAction):
        try:
            await opc_model.proxy_action(action)
        except KeyError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Failed to locate target feature: {e!s}",
            )
        except Exception as e:  # used to capture all ua exceptions out there
            logger.exception("Failed to apply action")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to apply action: {e!s}",
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
