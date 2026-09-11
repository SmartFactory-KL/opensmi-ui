from typing import List
import uuid
from fastapi import APIRouter, HTTPException

from model.node_types import MachineDto
from opc_client.server_module import ServerModule

router = APIRouter(prefix="/api/machine", tags=["machine"])

server_module = ServerModule()


@router.get("/")
async def request_server_machine_list() -> List[MachineDto]:
    """
    Get all machines and their data from the currently connected OPC UA
    """
    return await server_module.get_machine_list()


@router.get("/lock/{machine_entity_id}/toggle")
async def request_lock_toggle(machine_entity_id: str):
    """
    Request to `lock` the machine identified by `machine_entity_id`
    """
    try:
        server_module.check_pin_guard()

        target_machine = server_module.get_machine(uuid.UUID(machine_entity_id))
        if target_machine is not None:
            await target_machine.get_lock().request_lock_toggle()
        else:
            raise Exception(f"Machine for entityId ${machine_entity_id} not found!")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lock/{machine_entity_id}/break")
async def request_lock_break(machine_entity_id: str):
    """
    Request to `break` an already existing lock for the machine identified by `machine_entity_id`. Only works if the user has higher priority.
    """
    try:
        server_module.check_pin_guard()

        target_machine = server_module.get_machine(uuid.UUID(machine_entity_id))
        if target_machine is not None:
            await target_machine.get_lock().request_lock_break()
        else:
            raise Exception(f"Machine for entityId ${machine_entity_id} not found!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
