from fastapi import Response, status
from fastapi.routing import APIRouter

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.common import ModuleDisabledError
from opensmi_ui.pin_guard.pin_guard import PinGuard, PinGuardUnlockRequest

logger = get_module_logger("pin_guard_api")


def create_ping_guard_api(pin_guard: PinGuard) -> APIRouter:
    router = APIRouter(prefix="/api/pin-guard", tags=["pin-guard"])

    @router.get("/state", summary="Get PinGuard State")
    async def get_state():
        state = pin_guard.get_state()
        return state

    @router.post("/lock", summary="Request the PinGuard to be locked")
    async def post_lock(response: Response):
        # locking does not need a pin
        try:
            pin_guard.request_lock()
        except ModuleDisabledError:
            return Response(
                status_code=status.HTTP_409_CONFLICT, content="PinGuard is not enabled"
            )
        except Exception:
            logger.exception("Failed to lock PinGuard")

            return Response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content="Failed to lock due to an unexpected server error",
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post(
        "/unlock",
        summary="Request the PinGuard to be unlocked using a PinGuardUnlockRequest",
    )
    async def post_unlock(request: PinGuardUnlockRequest, response: Response):
        # locking does not need a pin
        try:
            pin_guard.request_unlock(pin_input=request)
        except ModuleDisabledError:
            return Response(
                status_code=status.HTTP_409_CONFLICT, content="PinGuard is not enabled"
            )
        except ValueError:
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED, content="Incorrect PIN"
            )
        except Exception:
            logger.exception("Failed to unlock PinGuard")

            return Response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content="Failed to unlock due to an unexpected server error",
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
