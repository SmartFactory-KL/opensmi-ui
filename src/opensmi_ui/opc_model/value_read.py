import base64
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from asyncua import ua


class VariantNormalizationFailedError(RuntimeError):
    """Raised whenever a value could not be normalized to Variant type"""


def normalize_to_variant(input: Any) -> ua.Variant | None:
    if input is None:
        return None

    if isinstance(input, ua.Variant):
        return input

    if isinstance(input, ua.DataValue):
        return input.Value

    raise VariantNormalizationFailedError(
        f"Input of type {type(input)} could not be normalized to Variant"
    )


def _value_to_string(value: object) -> str:
    if value is None:
        return "None"

    if isinstance(value, str):
        return value

    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, ua.StatusCode):
        return value.name

    if isinstance(value, Enum):
        return value.name or str(value.value)

    if isinstance(value, ua.XmlElement):
        return value.Value

    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_value_to_string(v) for v in value) + "]"

    if isinstance(value, ua.Variant):
        return variant_value_to_string(value)

    if isinstance(value, ua.DataValue):
        return variant_value_to_string(value.Value)

    # Includes numeric values, booleans, NodeIds, QualifiedNames,
    # LocalizedText, ExpandedNodeIds, and generated UA structures.
    return str(value)


def variant_value_to_string(input: ua.Variant | None) -> str:
    if input is None or input.Value is None:
        return "None"

    return _value_to_string(input.Value)
