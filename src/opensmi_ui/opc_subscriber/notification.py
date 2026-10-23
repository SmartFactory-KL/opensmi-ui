from datetime import datetime
from typing import Any

from asyncua import ua
from asyncua.common.events import Event
from pydantic.alias_generators import to_snake

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.opc_types import LocalizedTextData, NodeIdData, VariantData

logger = get_module_logger("opc_subscriber.notification")


class NotificationEvent(JsonOutModel):
    event_id: str
    event_type: NodeIdData
    source_node: NodeIdData
    source_name: str

    time: datetime
    message: LocalizedTextData
    severity: int


def read_notification(event: Event) -> NotificationEvent | None:
    if event is None or event.event_fields is None or event.select_clauses is None:
        return None

    if len(event.event_fields) != len(event.select_clauses):
        logger.warning(
            f"Event field length mismatch: {len(event.event_fields)} != {len(event.select_clauses)}"
        )
        return None

    vals: dict[str, Any] = {}

    for idx, evt_field in enumerate(event.event_fields):
        select_clause = event.select_clauses[idx]

        if len(select_clause.BrowsePath) < 1:
            continue

        first_browse_path = select_clause.BrowsePath[0]

        if not isinstance(first_browse_path, ua.QualifiedName):
            continue

        attr_name = to_snake(first_browse_path.Name)
        if attr_name in NotificationEvent.model_fields:
            vals[attr_name] = VariantData.from_ua(value=evt_field).value

    notification = NotificationEvent.model_validate(vals)

    return notification
