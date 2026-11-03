from collections.abc import Callable
from datetime import datetime
from typing import Any

from asyncua import ua
from asyncua.common.subscription import DataChangeEvent

from opensmi_ui.model.json import JsonOutModel
from opensmi_ui.opc_model.entities.entity import FeatureNodeEntity
from opensmi_ui.opc_model.opc_types import VariantData
from opensmi_ui.opc_model.value_read import normalize_to_variant


def handle_update_with_callback(
    evt: DataChangeEvent,
    update_creator: Callable[[Any, datetime | None], JsonOutModel],
    entity: FeatureNodeEntity | None,
    callback: Callable[[JsonOutModel], None],
):
    if not isinstance(entity, FeatureNodeEntity):
        raise TypeError(
            f"Entity is not of type FeatureNodeEntity but of type {type(entity)}"
        )

    data_value = evt.data.monitored_item.Value
    if not isinstance(data_value, ua.DataValue):
        raise TypeError("Received unexpected Non-DataValue Update")

    value = normalize_to_variant(data_value)
    if not isinstance(value, ua.Variant):
        raise TypeError("Received unexpected Non-Variant Update")

    data = VariantData.from_ua(value)
    update = update_creator(data.value, (data_value.SourceTimestamp))

    entity.apply_update(update)

    callback(update)
