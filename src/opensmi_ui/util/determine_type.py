import logging
from typing import Any

from pyuaadapter.client.remote_variable import RemoteVariable

from model.node_types import RemoteVariableValueType

logger = logging.getLogger("uvicorn")

IMAGE_TYPE_LIST = [
    "ImageJPG",
    "ImagePNG",
    "ImageBMP",
    "ImageGIF",
]


class RemoteVariableTypeAnnotationResult:
    value_type: RemoteVariableValueType
    value_annotation: Any


def determine_type_and_annotations(
    remote_variable: RemoteVariable, ua_data_type: str = ""
) -> RemoteVariableTypeAnnotationResult:
    result = RemoteVariableTypeAnnotationResult()

    result.value_type = RemoteVariableValueType.Text
    result.value_annotation = None

    if len(ua_data_type) > 0:
        if ua_data_type in IMAGE_TYPE_LIST:
            # if this changes, remember to also update the "on_..._update" methods -
            # in there you only have access to the RemoteVariable,
            # but not (yet) the RemoteVariable Module
            result.value_type = ua_data_type
            result.value_annotation = ua_data_type

    if len(remote_variable.valid_values) != 0:
        result.value_type = RemoteVariableValueType.Enum
        result.value_annotation = remote_variable.valid_values
        return result
    elif remote_variable.range is not None:
        result.value_type = RemoteVariableValueType.FloatRange
        result.value_annotation = remote_variable.range
        return result

    # check the actual datatype
    if isinstance(remote_variable.value, bool):
        result.value_type = RemoteVariableValueType.Boolean
        result.value_annotation = None

    return result
