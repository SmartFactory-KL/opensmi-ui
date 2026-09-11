from typing import Any

from asyncua.ua import LocalizedText, NodeId, VariantType


def convert_string_to_variant(
    input: str, variant: int, value_type: type | None = None
) -> Any:
    if input is None:
        return None

    match variant:
        # None
        ## not used, as None input would be null and is already satisfied
        # boolean
        case VariantType.Boolean:
            return convert_string_to_bool(input=str(input))
        # ints
        case VariantType.Int16:
            return convert_string_to_int(input=str(input))
        case VariantType.Int32:
            return convert_string_to_int(input=str(input))
        case VariantType.Int64:
            return convert_string_to_int(input=str(input))
        # uints
        case VariantType.UInt16:
            return convert_string_to_uint(input=str(input))
        case VariantType.UInt32:
            return convert_string_to_uint(input=str(input))
        case VariantType.UInt64:
            return convert_string_to_uint(input=str(input))
        # floats
        case VariantType.Float:
            return convert_string_to_float(input=str(input))
        case VariantType.Double:
            return convert_string_to_float(input=str(input))
        case VariantType.NodeId:
            return input
        # string
        case VariantType.String:
            return input
        # variant
        case VariantType.Variant:
            if value_type is not None:
                return convert_string_to_type(input, value_type)
            else:
                raise Exception(
                    "Cannot convert to VariantType.Variant when no value_type is set"
                )

    raise Exception("Conversion to VariantType " + str(variant) + " not supported")


def convert_string_to_type(input: str, value_type: type) -> Any:
    if input is None:
        return None

    if value_type is float:
        return convert_string_to_float(input)

    if value_type is int:
        return convert_string_to_int(input)

    if value_type is str:
        return input

    if value_type is bool:
        return convert_string_to_bool(input)

    raise Exception(f"Invalid input type {value_type}")


def convert_string_to_float(input: str) -> float:
    try:
        return float(input)
    except Exception as _:
        raise Exception("Cannot convert input to float")


def convert_string_to_int(input: str) -> int:
    try:
        return int(input)
    except Exception as _:
        raise Exception("Cannot convert input to int")


def convert_string_to_uint(input: str) -> int:
    try:
        val = int(input)
        if val != abs(val):
            raise Exception("Uint cannot be negative")
        return val
    except Exception as _:
        raise Exception("Cannot convert input to uint")


def convert_string_to_bool(input: str) -> bool:
    try:
        if input.lower() in ["true", "on", "1"]:
            return True
        elif input.lower() in ["false", "off", "0"]:
            return False
        raise Exception()
    except Exception as _:
        raise Exception("Cannot convert input to bool")


def convert_value_to_simple(input: Any) -> str:
    if input is None:
        return None

    if isinstance(input, (bool, int, float, str)):
        return input
    elif isinstance(input, LocalizedText):
        return input.Text
    elif isinstance(input, NodeId):
        return input.to_string() if not input.is_null() else None

    return str(input)
