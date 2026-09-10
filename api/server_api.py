from uuid import UUID
from fastapi import APIRouter, HTTPException

import app_config
from model.common_types import GenericActionRequest
from model.pin_guard_types import PinGuardUnlockRequest
from model.server_types import (
    ServerConnectRequest,
    ServerDefaultConnectionDataResponse,
    ServerStateResponse,
)
from opc_client.server_module import ServerModule

router = APIRouter(prefix="/api/server", tags=["server"])

server_module = ServerModule()


@router.get("/")
async def request_server_state() -> ServerStateResponse:
    """
    Get data about the current connection from module-ui-backend to OPC UA
    """
    return server_module.get_server_state()


@router.get("/default-connection-data")
async def get_default_connection_data() -> ServerDefaultConnectionDataResponse:
    """
    Get default connection data set by server environment (might be empty)
    """
    return server_module.get_default_connection_data()


@router.post("/connect")
async def request_connect(data: ServerConnectRequest):
    """
    Request a new connection to the server with the given data.
    """
    try:
        return await server_module.request_connect(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect")
async def request_disconnect(force: bool = False):
    """
    Request a disconnect from the current OPC UA. The `force` option is reserved for internal usage and should not be considered part of the API.
    """
    await server_module.request_disconnect(force)


@router.get("/pin-guard")
async def request_pin_state():
    """
    Request the current state of the PinGuard
    """
    return server_module.get_pin_guard().get_state()


@router.post("/pin-guard/unlock")
async def request_pin_unlock(pin_input: PinGuardUnlockRequest):
    """
    If PinGuard is enabled, this will try to unlock it with pin input.
    """
    try:
        server_module.get_pin_guard().request_unlock_with_pin(pin_input=pin_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pin-guard/lock")
async def request_pin_lock():
    """If PinGuard is enabled, it can be locked with this endpoint."""
    try:
        server_module.get_pin_guard().request_lock()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/action")
async def request_skill_action(action: GenericActionRequest):
    """
    Request to trigger a GenericAction. This is on the server API and will be proxied to the target machine.
    """
    try:
        return await server_module.proxy_action(action=action)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/info")
async def request_debug_information():
    """Request debugging info. Passwords/Pins are masked."""
    try:
        return app_config.get_masked_configuration()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/node-history/{node_entity_id}")
async def request_node_history(
    node_entity_id: UUID, limit: int = 100, timedelta_hours: int = 1
):
    """
    Request the history of data of a node from within the last hour, sorted in time ascending order, limited to limit and timedelta_hours.
    """
    try:
        return await server_module.request_node_history(
            node_entity_id=node_entity_id, limit=limit, timedelta_hours=timedelta_hours
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
