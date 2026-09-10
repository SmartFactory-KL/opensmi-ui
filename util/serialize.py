import base64
import logging
from typing import Any
from asyncua.ua import DataValue, Variant, VariantType, StatusCodes, NodeId
from datetime import datetime

from model.node_types import SimpleDataValueDto, VariantValueDto
from util.stats_counter import StatsCounter

logger = logging.getLogger("uvicorn")

stats_counter = StatsCounter()


def serialize_data_value(data_value: DataValue | None) -> SimpleDataValueDto:
    if data_value is None:
        return SimpleDataValueDto(
            status_code=StatusCodes.BadNoData,
            timestamp=datetime.now().timestamp(),
            value=serialize_variant_value(None),
        )

    result = SimpleDataValueDto(
        status_code=data_value.StatusCode.value,
        timestamp=data_value.ServerTimestamp.timestamp(),
        value=serialize_variant_value(data_value.Value),
    )
    return result


def serialize_variant_value(input: Variant | None) -> VariantValueDto:
    if input is None:
        return VariantValueDto(
            variant_type=VariantType.Null, value=None, dimensions=None
        )

    result = VariantValueDto(
        variant_type=input.VariantType,
        dimensions=input.Dimensions,
        value=encode_variant_value_value(input.Value),
    )
    return result


def encode_variant_value_value(input: Any) -> Any:
    """
    Takes a any input, returns a serialized value to be used for the value field of a Variant.
    """
    if input is None:
        stats_counter.add_serialization_tick("NullType")
        return None

    if isinstance(input, bytes):
        input = Variant(input, VariantType=VariantType.ByteString)

    if isinstance(input, NodeId):
        # input = Variant(input.to_string(), VariantType=VariantType.NodeId)
        return input.to_string()

    # This is the "catch-all" for non-variant inputs
    # all non-variant inputs will simply be returned here
    # so deal with them above if needed
    if not isinstance(input, Variant):
        stats_counter.add_serialization_tick(type(input).__name__)
        return input

    # from this point onwards, input should be a Variant
    stats_counter.add_serialization_tick("VT: " + input.VariantType.name)
    match input.VariantType:
        case VariantType.Null:
            return None

        # All integer-like types → int
        case (
            VariantType.SByte
            | VariantType.Byte
            | VariantType.Int16
            | VariantType.UInt16
            | VariantType.Int32
            | VariantType.UInt32
            | VariantType.Int64
            | VariantType.UInt64
            | VariantType.StatusCode
        ):
            return int(input.Value)

        # Boolean
        case VariantType.Boolean:
            return bool(input.Value)

        # Floating-point types → float
        case VariantType.Float | VariantType.Double:
            return float(input.Value)

        # NodeIds
        case VariantType.NodeId | VariantType.ExpandedNodeId:
            # return NodeId(input).to_string()
            # FIXME: This does not seem to work at all?
            return NodeId(input.Value).to_string()

        # String-like types → str
        case (
            VariantType.String  # obvious
            | VariantType.XmlElement  # never seen?
            | VariantType.QualifiedName
            | VariantType.LocalizedText  # not sure here
            | VariantType.DiagnosticInfo
        ):
            return str(input.Value)

        # DateTime
        case VariantType.DateTime:
            return input.Value.isoformat() if input.Value else None

        # Guid
        case VariantType.Guid:
            return str(input.Value)

        # ByteString
        case VariantType.ByteString:
            # FIXME: should be probably base64
            # return input.Value.hex() if input.Value is not None else None
            if input.Value is None:
                return None
            try:
                return base64.b64encode(input.Value).decode("ascii")
            except Exception as e:
                logger.warning("Unable to convert ByteString to base64")
                logger.warning(input.Value)
                logger.warning(e)
                return None

        # ExtensionObject
        case VariantType.ExtensionObject:
            return (
                input.Value.to_dict()
                if hasattr(input.Value, "to_dict")
                else str(input.Value)
            )

        # DataValue
        case VariantType.DataValue:
            return serialize_data_value(input.Value)

        # Nested Variant
        case VariantType.Variant:
            return encode_variant_value_value(input.Value)

        case _:
            raise ValueError(f"Unsupported VariantType: {input.VariantType}")
