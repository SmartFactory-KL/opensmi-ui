import dataclasses
import math
from base64 import b64decode, b64encode
from collections.abc import Sequence
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Literal, Union, cast
from uuid import UUID

from asyncua import ua

from opensmi_ui.model.json import JsonOutModel

VT = ua.VariantType

SMALL_INT_TYPES = {VT.SByte, VT.Byte, VT.Int16, VT.UInt16, VT.Int32, VT.UInt32}
BIG_INT_TYPES = {VT.Int64, VT.UInt64}
"""Big Ints could be bigger than MAX_SAFE_INTEGER for JSON/JS so they are encoded as strings"""
FLOAT_TYPES = {VT.Float, VT.Double}

MAX_SAFE_INTEGER = 2**53 - 1


class QualifiedNameData(JsonOutModel):
    name: str
    namespace_index: int

    @classmethod
    def from_ua(cls, value: ua.QualifiedName) -> "QualifiedNameData":
        return cls(
            name=value.Name,
            namespace_index=value.NamespaceIndex,
        )

    def to_ua(self) -> ua.QualifiedName:
        return ua.QualifiedName(Name=self.name, NamespaceIndex=self.namespace_index)


class LocalizedTextData(JsonOutModel):
    text: str | None
    locale: str | None

    @classmethod
    def from_ua(cls, value: ua.LocalizedText) -> "LocalizedTextData":
        return cls(
            text=value.Text,
            locale=value.Locale,
        )

    def to_ua(self) -> ua.LocalizedText:
        return ua.LocalizedText(Text=self.text, Locale=self.locale)


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

    def to_ua(self) -> ua.ExpandedNodeId:
        return _to_expanded(self.node_id.to_ua(), self.namespace_uri, self.server_index)


class ReferenceData(JsonOutModel):
    reference_type_id: NodeIdData
    is_forward: bool
    node_id: NodeIdData
    browse_name: QualifiedNameData
    display_name: LocalizedTextData
    node_class: str
    type_definition: NodeIdData | None

    @classmethod
    def from_ua(cls, ref: ua.ReferenceDescription) -> "ReferenceData":
        return cls(
            reference_type_id=NodeIdData.from_ua(ref.ReferenceTypeId),
            is_forward=ref.IsForward,
            node_id=NodeIdData.from_ua(ref.NodeId),
            browse_name=QualifiedNameData.from_ua(ref.BrowseName),
            display_name=LocalizedTextData.from_ua(ref.DisplayName),
            node_class=ref.NodeClass.name,
            type_definition=(
                NodeIdData.from_ua(ref.TypeDefinition)
                if ref.TypeDefinition is not None and not ref.TypeDefinition.is_null()
                else None
            ),
        )

    def to_ua(self) -> ua.ReferenceDescription:
        return ua.ReferenceDescription(
            ReferenceTypeId=self.reference_type_id.to_ua(),
            IsForward=self.is_forward,
            # asyncua declares this field as ExpandedNodeId
            NodeId=_to_expanded(self.node_id.to_ua()),
            BrowseName=self.browse_name.to_ua(),
            DisplayName=self.display_name.to_ua(),
            NodeClass=ua.NodeClass[self.node_class],
            # from_ua() maps a null TypeDefinition to None, so map it back
            TypeDefinition=(
                self.type_definition.to_ua() if self.type_definition else ua.NodeId()
            ),
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

    def to_ua(self) -> ua.StatusCode:
        # name and severity are derived from the code, so only the code is used
        return ua.StatusCode(ua.UInt32(self.code))


class DiagnosticInfoData(JsonOutModel):
    """A ua.DiagnosticInfo. The first four fields are indexes into the string
    table of the response they came from, not strings."""

    symbolic_id: int | None = None
    namespace_uri: int | None = None
    locale: int | None = None
    localized_text: int | None = None
    additional_info: str | None = None
    inner_status_code: StatusCodeData | None = None
    inner_diagnostic_info: Union["DiagnosticInfoData", None] = None

    @classmethod
    def from_ua(cls, value: ua.DiagnosticInfo) -> "DiagnosticInfoData":
        inner_status = getattr(value, "InnerStatusCode", None)
        inner_info = getattr(value, "InnerDiagnosticInfo", None)

        return cls(
            symbolic_id=getattr(value, "SymbolicId", None),
            namespace_uri=getattr(value, "NamespaceURI", None),
            locale=getattr(value, "Locale", None),
            localized_text=getattr(value, "LocalizedText", None),
            additional_info=getattr(value, "AdditionalInfo", None),
            inner_status_code=(
                StatusCodeData.from_ua(inner_status)
                if inner_status is not None
                else None
            ),
            inner_diagnostic_info=(
                DiagnosticInfoData.from_ua(inner_info)
                if inner_info is not None
                else None
            ),
        )

    def to_ua(self) -> ua.DiagnosticInfo:
        kwargs: dict[str, Any] = {}
        if self.symbolic_id is not None:
            kwargs["SymbolicId"] = self.symbolic_id
        if self.namespace_uri is not None:
            kwargs["NamespaceURI"] = self.namespace_uri
        if self.locale is not None:
            kwargs["Locale"] = self.locale
        if self.localized_text is not None:
            kwargs["LocalizedText"] = self.localized_text
        if self.additional_info is not None:
            kwargs["AdditionalInfo"] = self.additional_info
        if self.inner_status_code is not None:
            kwargs["InnerStatusCode"] = self.inner_status_code.to_ua()
        if self.inner_diagnostic_info is not None:
            kwargs["InnerDiagnosticInfo"] = self.inner_diagnostic_info.to_ua()
        return ua.DiagnosticInfo(**kwargs)


class ExtensionObjectData(JsonOutModel):
    """A ua.ExtensionObject, i.e. a structure.

    Decoded structures (asyncua has a class for them, e.g. Range, EUInformation,
    Argument) have `members`, keyed by the OPC UA field name, and `type_id` is the
    NodeId of the DataType.

    Structures asyncua cannot decode have `body` (Base64 of the raw bytes) and
    `type_id` is the NodeId of the encoding.
    """

    type_name: str | None = None
    type_id: NodeIdData | None = None
    members: dict[str, Any] | None = None
    body: str | None = None

    @classmethod
    def from_ua(cls, value: Any) -> "ExtensionObjectData":
        # undecoded: asyncua keeps the raw bytes in a generic ExtensionObject
        if isinstance(value, ua.ExtensionObject):
            type_id = getattr(value, "TypeId", None)
            body = getattr(value, "Body", None)
            return cls(
                type_id=(
                    NodeIdData.from_ua(type_id)
                    if isinstance(type_id, ua.NodeId)
                    else None
                ),
                body=(
                    b64encode(bytes(body)).decode("ascii") if body is not None else None
                ),
            )

        # decoded: asyncua generates a dataclass per structure
        if dataclasses.is_dataclass(value) and not isinstance(value, type):
            member_types = _ua_member_types(value)
            data_type = getattr(value, "data_type", None)
            return cls(
                type_name=type(value).__name__,
                type_id=(
                    NodeIdData.from_ua(data_type)
                    if isinstance(data_type, ua.NodeId)
                    else None
                ),
                members={
                    field.name: encode_member(
                        getattr(value, field.name), member_types.get(field.name)
                    )
                    for field in dataclasses.fields(value)
                },
            )

        raise ValueError(
            f"Cannot encode ExtensionObject of type {type(value)}: Not supported"
        )

    def to_ua(self) -> Any:
        # undecoded: raw bytes + encoding id
        if self.members is None:
            if self.body is None and self.type_id is None:
                raise ValueError("ExtensionObject needs either members or body/type_id")
            return ua.ExtensionObject(
                TypeId=self.type_id.to_ua() if self.type_id else ua.NodeId(),
                Body=(
                    cast(ua.ByteString, b64decode(self.body, validate=True))
                    if self.body is not None
                    else None
                ),
            )

        # decoded: look up asyncua's generated dataclass by name
        struct_cls: Any = getattr(ua, self.type_name, None) if self.type_name else None
        if not isinstance(struct_cls, type) or not dataclasses.is_dataclass(struct_cls):
            raise ValueError(
                f"Cannot decode ExtensionObject: unknown structure {self.type_name!r}"
            )

        member_types = _ua_member_types(struct_cls)
        return struct_cls(
            **{
                name: decode_member(value, member_types.get(name))
                for name, value in self.members.items()
            }
        )


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

    def to_ua(self) -> ua.DataValue:
        kwargs: dict[str, Any] = {
            "Value": self.value.to_ua() if self.value is not None else None,
            "SourceTimestamp": self.source_timestamp,
            "ServerTimestamp": self.server_timestamp,
            "SourcePicoseconds": self.source_picoseconds,
            "ServerPicoseconds": self.server_picoseconds,
        }
        if self.status is not None:
            kwargs["StatusCode_"] = self.status.to_ua()
        return ua.DataValue(**kwargs)


class VariantData(JsonOutModel):
    """A ua.Variant with an explicit type tag.

    `value` depends on `type`; nested types hold the models above. Arrays are
    lists, multi-dimensional arrays are nested lists with the shape in
    `dimensions`.
    """

    type: str  # name of ua.VariantType, e.g. "Int32"
    is_array: bool = False
    dimensions: Sequence[int] | None = None
    value: Any = None

    @classmethod
    def from_ua(cls, value: ua.Variant) -> "VariantData":
        if not isinstance(value, ua.Variant):
            # you never know what value could actually be :)
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
            return cls(
                type=source_variant_type.name,
                is_array=True,
                dimensions=multi_dim,
                value=encode_array(source_variant_type, source_value),
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

    def to_ua(self) -> ua.Variant:
        try:
            variant_type = ua.VariantType[self.type]
        except KeyError:
            raise ValueError(f"Unknown VariantType {self.type!r}") from None

        if self.is_array:
            if not isinstance(self.value, (list, tuple)):
                raise ValueError("Array variant value must be a list")
            values = decode_array(variant_type, self.value)
            dimensions = list(self.dimensions) if self.dimensions else None
            if dimensions:
                # asyncua keeps multi-dimensional arrays flat, shape in Dimensions
                values = _flatten(values)
                expected = math.prod(dimensions)
                if len(values) != expected:
                    raise ValueError(
                        f"Array has {len(values)} elements, dimensions {dimensions} "
                        f"require {expected}"
                    )
            return ua.Variant(
                Value=values,
                VariantType=variant_type,
                Dimensions=cast(list[ua.Int32], dimensions)
                if dimensions is not None
                else None,
                is_array=True,
            )

        return ua.Variant(
            Value=decode_scalar(variant_type, self.value),
            VariantType=variant_type,
            is_array=False,
        )


def encode_array(variant_type: ua.VariantType, values: Sequence[Any]) -> list[Any]:
    """Encodes a (possibly nested, for multi-dimensional arrays) list of values."""
    return [
        encode_array(variant_type, item)
        if isinstance(item, (list, tuple))
        else encode_scalar(variant_type, item)
        for item in values
    ]


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
        case VT.ExtensionObject:
            return ExtensionObjectData.from_ua(value)
        case VT.DataValue:
            return DataValueData.from_ua(value)
        case VT.Variant:
            return VariantData.from_ua(value)
        case VT.DiagnosticInfo:
            return DiagnosticInfoData.from_ua(value)
        case _:
            raise ValueError(
                f"Cannot encode VariantType {variant_type}: Not supported",
            )


def encode_member(value: Any, type_name: str | None = None) -> Any:
    """Encodes a field of a structure.

    Unlike a Variant, a structure field carries no VariantType tag. If asyncua
    knows the declared type name of the field (`ListOfInt64`, `Double`, ...) it is
    used, so Int64 fields are encoded as strings like they are in a Variant.
    Otherwise the encoding is chosen by the Python type of the value.
    """
    if value is None:
        return None

    element_type = type_name.removeprefix("ListOf") if type_name else None

    if isinstance(value, (list, tuple)):
        return [encode_member(item, element_type) for item in value]

    if element_type is not None and element_type in VT.__members__:
        return encode_scalar(VT[element_type], value)

    return _encode_by_python_type(value)


def _encode_by_python_type(value: Any) -> Any:
    # order matters: bool is an int, ExpandedNodeId is a NodeId, and the ua types
    # are dataclasses themselves, so the generic structure case has to come last
    if isinstance(value, bool):
        return value
    if isinstance(value, int):  # also covers IntEnum
        as_int = int(value)
        return str(as_int) if abs(as_int) > MAX_SAFE_INTEGER else as_int
    if isinstance(value, Enum):
        return _encode_by_python_type(value.value)
    if isinstance(value, float):
        return _encode_float(value)
    if isinstance(value, str):
        return value
    if isinstance(value, (bytes, bytearray)):
        return b64encode(bytes(value)).decode("ascii")
    if isinstance(value, datetime):
        return _to_utc(value).isoformat()  # type: ignore[union-attr]
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, ua.ExpandedNodeId):
        return ExpandedNodeIdData.from_ua(value)
    if isinstance(value, ua.NodeId):
        return NodeIdData.from_ua(value)
    if isinstance(value, ua.QualifiedName):
        return QualifiedNameData.from_ua(value)
    if isinstance(value, ua.LocalizedText):
        return LocalizedTextData.from_ua(value)
    if isinstance(value, ua.StatusCode):
        return StatusCodeData.from_ua(value)
    if isinstance(value, ua.Variant):
        return VariantData.from_ua(value)
    if isinstance(value, ua.DataValue):
        return DataValueData.from_ua(value)
    if isinstance(value, ua.DiagnosticInfo):
        return DiagnosticInfoData.from_ua(value)
    if isinstance(value, ua.ExtensionObject) or (
        dataclasses.is_dataclass(value) and not isinstance(value, type)
    ):
        return ExtensionObjectData.from_ua(value)

    raise ValueError(f"Cannot encode value of type {type(value)}: Not supported")


def _ua_member_types(structure: Any) -> dict[str, str]:
    """Declared field types of a generated asyncua structure, by field name."""
    ua_types = getattr(type(structure), "ua_types", None)
    if not ua_types:
        return {}
    if isinstance(ua_types, dict):
        return dict(ua_types)
    try:
        return {entry[0]: entry[1] for entry in ua_types}
    except (TypeError, IndexError):
        return {}


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


def _model(model_cls: type, value: Any) -> Any:
    """Nested values are models when built in Python, but plain dicts when the
    outer model was parsed from JSON."""
    if isinstance(value, model_cls):
        return value
    return model_cls.model_validate(value)


def decode_array(variant_type: ua.VariantType, values: Sequence[Any]) -> list[Any]:
    return [
        decode_array(variant_type, item)
        if isinstance(item, (list, tuple))
        else decode_scalar(variant_type, item)
        for item in values
    ]


def decode_scalar(variant_type: ua.VariantType, value: Any) -> Any:
    if value is None:
        return None

    if variant_type in SMALL_INT_TYPES or variant_type in BIG_INT_TYPES:
        return int(value)  # big ints arrive as strings
    if variant_type in FLOAT_TYPES:
        return _decode_float(value)

    match variant_type:
        case VT.Null:
            return None
        case VT.Boolean:
            return bool(value)
        case VT.String | VT.XmlElement:
            return str(value)
        case VT.DateTime:
            if isinstance(value, str):
                value = datetime.fromisoformat(value)
            return _to_utc(value)
        case VT.Guid:
            return UUID(str(value))
        case VT.ByteString:
            return b64decode(value, validate=True)
        case VT.NodeId:
            return _model(NodeIdData, value).to_ua()
        case VT.ExpandedNodeId:
            return _model(ExpandedNodeIdData, value).to_ua()
        case VT.QualifiedName:
            return _model(QualifiedNameData, value).to_ua()
        case VT.LocalizedText:
            return _model(LocalizedTextData, value).to_ua()
        case VT.StatusCode:
            return _model(StatusCodeData, value).to_ua()
        case VT.ExtensionObject:
            return _model(ExtensionObjectData, value).to_ua()
        case VT.DataValue:
            return _model(DataValueData, value).to_ua()
        case VT.Variant:
            return _model(VariantData, value).to_ua()
        case VT.DiagnosticInfo:
            return _model(DiagnosticInfoData, value).to_ua()
        case _:
            raise ValueError(
                f"Cannot decode VariantType {variant_type}: Not supported",
            )


def decode_member(value: Any, type_name: str | None = None) -> Any:
    """Inverse of encode_member(). Needs the declared field type to undo the
    lossy encodings (Int64 -> str, bytes -> Base64, ...). Without it the value
    is returned unchanged."""
    if value is None:
        return None

    element_type = type_name.removeprefix("ListOf") if type_name else None

    if isinstance(value, (list, tuple)):
        return [decode_member(item, element_type) for item in value]

    if element_type is None:
        return value

    if element_type in VT.__members__:
        return decode_scalar(VT[element_type], value)

    named = getattr(ua, element_type, None)
    if isinstance(named, type):
        if issubclass(named, Enum):
            return named(value)
        if dataclasses.is_dataclass(named):  # nested structure
            return _model(ExtensionObjectData, value).to_ua()

    return value


def _to_expanded(
    node_id: ua.NodeId, namespace_uri: str | None = None, server_index: int = 0
) -> ua.ExpandedNodeId:
    return ua.ExpandedNodeId(
        Identifier=node_id.Identifier,
        NamespaceIndex=node_id.NamespaceIndex,
        NodeIdType=node_id.NodeIdType,
        NamespaceUri=cast(ua.String, namespace_uri)
        if namespace_uri is not None
        else None,
        ServerIndex=ua.Int32(server_index),
    )


def _flatten(values: Sequence[Any]) -> list[Any]:
    flat: list[Any] = []
    for item in values:
        if isinstance(item, (list, tuple)):
            flat.extend(_flatten(item))
        else:
            flat.append(item)
    return flat


def _decode_float(value: Any) -> float:
    if value == "NaN":
        return math.nan
    if value == "Infinity":
        return math.inf
    if value == "-Infinity":
        return -math.inf
    return float(value)
