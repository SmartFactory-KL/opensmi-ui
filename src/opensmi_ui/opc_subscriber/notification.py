from datetime import datetime
from typing import Any

from asyncua import ua
from asyncua.common.events import Event
from pydantic.alias_generators import to_snake

from opensmi_ui.logger import get_module_logger
from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.opc_types import LocalizedTextData, NodeIdData, VariantData
from opensmi_ui.opc_session.namespace import (
    DefaultNamespaceURI,
    OPCNamespace,
    UriNodeId,
)

logger = get_module_logger("opc_subscriber.notification")

SFKL_ALERT_TYPE = UriNodeId(
    Identifier=ua.Int32(1001),
    NamespaceUri=DefaultNamespaceURI.SFKL_MACHINE,
)

BASE_EVENT_TYPE = UriNodeId(
    Identifier=ua.Int32(ua.object_ids.ObjectIds.BaseEventType),
    NamespaceUri=DefaultNamespaceURI.OPC_UA_0,
)


class NotificationEvent(JsonOutModel):
    event_id: str
    event_type: NodeIdData

    source_node: NodeIdData
    source_name: str

    time: datetime
    message: LocalizedTextData
    severity: int


class NotificationAlert(NotificationEvent):
    error_code: str | None


def read_notification(
    opc_namespace: OPCNamespace, event: Event
) -> NotificationEvent | None:
    if event is None or event.event_fields is None or event.select_clauses is None:
        return None

    if len(event.event_fields) != len(event.select_clauses):
        logger.warning(
            f"Event field length mismatch: {len(event.event_fields)} != {len(event.select_clauses)}"
        )
        return None

    raw_values: dict[str, Any] = {}
    event_type: ua.NodeId | None = None

    for idx, evt_field in enumerate(event.event_fields):
        select_clause = event.select_clauses[idx]

        if len(select_clause.BrowsePath) < 1:
            continue

        first_browse_path = select_clause.BrowsePath[0]

        if not isinstance(first_browse_path, ua.QualifiedName) or not isinstance(
            evt_field, ua.Variant
        ):
            continue

        # event_type has to be handled on its own as all values
        # will be in their "xxData" format and comparisons would be funky
        if first_browse_path.Name == "EventType":
            event_type = evt_field.Value

        raw = VariantData.from_ua(evt_field).value
        raw_values[to_snake(first_browse_path.Name)] = raw

    if event_type is None:
        logger.warning("Event Type was None")
        return None

    if event_type == opc_namespace.to_node_id(SFKL_ALERT_TYPE):
        return NotificationAlert.model_validate(raw_values)
    elif event_type == opc_namespace.to_node_id(BASE_EVENT_TYPE):
        return NotificationEvent.model_validate(raw_values)

    else:
        logger.warning(f"Received unknown EventType {event_type} on Notification")

    return None
