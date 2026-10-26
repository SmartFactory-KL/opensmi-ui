import math
from base64 import b64decode, b64encode
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Literal, Union, cast
from uuid import UUID

from asyncua import ua

from opensmi_ui.model.json import JsonOutModel

VT = ua.VariantType

SMALL_INT_TYPES = {VT.SByte, VT.Byte, VT.Int16, VT.UInt16, VT.Int32, VT.UInt32}
BIG_INT_TYPES = {VT.Int64, VT.UInt64}
"""Big Ints could be bigger than MAX_SAFE_INTEGER for JSON/JS so they are encoded as strings"""
FLOAT_TYPES = {VT.Float, VT.Double}


class QualifiedNameData(JsonOutModel):
    name: str
    namespace_index: int

    @classmethod
    def from_ua(cls, value: ua.QualifiedName) -> "QualifiedNameData":
        return cls(
            name=value.Name,
            namespace_index=value.NamespaceIndex,
        )


class LocalizedTextData(JsonOutModel):
    text: str | None
    locale: str | None

    @classmethod
    def from_ua(cls, value: ua.LocalizedText) -> "LocalizedTextData":
        return cls(
            text=value.Text,
            locale=value.Locale,
        )


class NodeIdData(JsonOutModel):
    identifier: str | int
    namespace_index: int
    identifier_type: str

    @classmethod
    def from_ua(cls, value: ua.NodeId) -> "NodeIdData":
        identifier = value.Identifier

        if isinstance(identifier, UUID):
            identifier = str(identifier)
        elif isinstance(identifier, bytes):
            identifier = b64encode(identifier).decode("ascii")

        return cls(
            identifier=identifier,
            namespace_index=value.NamespaceIndex,
            identifier_type=value.NodeIdType.name,
        )

    def to_ua(self) -> ua.NodeId:
        node_id_type = ua.NodeIdType[self.identifier_type]
        identifier: ua.Int32 | ua.String | ua.Guid | ua.ByteString

        if node_id_type == ua.NodeIdType.Guid:
            identifier = cast(ua.Guid, UUID(str(self.identifier)))
        elif node_id_type == ua.NodeIdType.ByteString:
            if not isinstance(self.identifier, str):
                raise ValueError("ByteString NodeId identifier must be a Base64 string")
            identifier = cast(ua.ByteString, b64decode(self.identifier, validate=True))
        elif node_id_type == ua.NodeIdType.Numeric:
            identifier = ua.Int32(int(self.identifier))
        else:
            identifier = ua.String(str(self.identifier))

        return ua.NodeId(
            Identifier=identifier,
            NamespaceIndex=ua.Int16(self.namespace_index),
            NodeIdType=node_id_type,
        )


class ExpandedNodeIdData(JsonOutModel):
    node_id: NodeIdData
    namespace_uri: str | None = None
    server_index: int = 0

    @classmethod
    def from_ua(cls, value: ua.ExpandedNodeId) -> "ExpandedNodeIdData":
        # ExpandedNodeId subclasses NodeId, so the NodeId part reads the same way
        return cls(
            node_id=NodeIdData.from_ua(value),
            namespace_uri=value.NamespaceUri,
            server_index=value.ServerIndex or 0,
        )


class StatusCodeData(JsonOutModel):
    code: int
    name: str | None = None
    # derived from the code, ignored by to_ua()
    severity: Literal["good", "uncertain", "bad"] = "good"

    @classmethod
    def from_ua(cls, value: ua.StatusCode) -> "StatusCodeData":
        try:
            name = value.name
        except (KeyError, ValueError, AttributeError):
            name = None  # code unknown to asyncua's lookup table

        if value.is_good():
            severity: Literal["good", "uncertain", "bad"] = "good"
        elif value.is_bad():
            severity = "bad"
        else:
            severity = "uncertain"

        return cls(code=int(value.value), name=name, severity=severity)


class DataValueData(JsonOutModel):
    value: Union["VariantData", None] = None
    status: StatusCodeData | None = None
    source_timestamp: datetime | None = None
    server_timestamp: datetime | None = None
    source_picoseconds: int | None = None
    server_picoseconds: int | None = None

    @classmethod
    def from_ua(cls, value: ua.DataValue) -> "DataValueData":
        status = getattr(value, "StatusCode_", None)
        return cls(
            value=VariantData.from_ua(value.Value) if value.Value is not None else None,
            status=StatusCodeData.from_ua(status) if status is not None else None,
            source_timestamp=_to_utc(value.SourceTimestamp),
            server_timestamp=_to_utc(value.ServerTimestamp),
            source_picoseconds=getattr(value, "SourcePicoseconds", None),
            server_picoseconds=getattr(value, "ServerPicoseconds", None),
        )


class VariantData(JsonOutModel):
    """A ua.Variant with an explicit type tag.

    `value` depends on `type` (see module docstring); nested types hold the
    models above. Multi-dimensional arrays are nested lists, with the shape
    in `dimensions`.
    """

    type: str  # name of ua.VariantType, e.g. "Int32"
    is_array: bool = False
    dimensions: Sequence[int] | None = None
    value: Any = None

    @classmethod
    def from_ua(cls, value: ua.Variant) -> "VariantData":
        if not isinstance(value, ua.Variant):
            raise TypeError(
                f"VariantData.from_ua cannot handle input of type {type(value)}"
            )

        source_variant_type = value.VariantType
        source_value = value.Value
        source_dimensions = list(value.Dimensions) if value.Dimensions else None
        multi_dim = (
            source_dimensions
            if source_dimensions and len(source_dimensions) > 1
            else None
        )

        if isinstance(source_value, (list, tuple)):
            value_list = [
                encode_scalar(source_variant_type, val) for val in source_value
            ]
            return cls(
                type=source_variant_type.name,
                is_array=True,
                dimensions=multi_dim,
                value=value_list,
            )

        return cls(
            type=source_variant_type.name,
            is_array=False,
            dimensions=None,
            value=encode_scalar(source_variant_type, source_value),
        )

    @classmethod
    def from_value(cls, value: Any) -> "VariantData":
        """For already unwrapped values; the type is inferred (int -> Int64, float -> Double)."""
        return cls.from_ua(ua.Variant(value))


def encode_scalar(variant_type: ua.VariantType, value: Any) -> Any:
    if value is None:
        return None

    if variant_type in SMALL_INT_TYPES:
        return int(value)
    if variant_type in BIG_INT_TYPES:
        return str(int(value))
    if variant_type in FLOAT_TYPES:
        return _encode_float(float(value))

    match variant_type:
        case VT.Null:
            return None
        case VT.Boolean:
            return bool(value)
        case VT.String | VT.XmlElement:
            return str(value)
        case VT.DateTime:
            return _to_utc(value).isoformat()  # type: ignore[union-attr]
        case VT.Guid:
            return str(value)
        case VT.ByteString:
            return b64encode(bytes(value)).decode("ascii")
        case VT.NodeId:
            return NodeIdData.from_ua(value)
        case VT.ExpandedNodeId:
            return ExpandedNodeIdData.from_ua(value)
        case VT.QualifiedName:
            return QualifiedNameData.from_ua(value)
        case VT.LocalizedText:
            return LocalizedTextData.from_ua(value)
        case VT.StatusCode:
            return StatusCodeData.from_ua(value)
        case VT.Variant:
            return VariantData.from_ua(value)
        case VT.DataValue:
            return DataValueData.from_ua(value)
        case _:
            raise ValueError(
                f"Cannot encode VariantType {variant_type}: Not supported",
            )


def _encode_float(x: float) -> float | str:
    if math.isnan(x):
        return "NaN"
    if math.isinf(x):
        return "Infinity" if x > 0 else "-Infinity"
    return x


def _to_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)  # OPC UA times are UTC
    return dt.astimezone(UTC)
