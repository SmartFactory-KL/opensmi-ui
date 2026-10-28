from datetime import datetime
from typing import Any

from asyncua import ua

from opensmi_ui.opc_model.entities.entity import (
    FeatureNodeEntity,
    FeatureNodeEntityData,
)
from opensmi_ui.opc_model.features.variable_modifier.modifier import (
    VariableModifierData,
)
from opensmi_ui.opc_model.features.variable_modifier.range_modifier import RangeModifier
from opensmi_ui.opc_model.features.variable_modifier.unit_modifier import UnitModifier
from opensmi_ui.opc_model.opc_node import OPCNode
from opensmi_ui.opc_model.opc_types import LocalizedTextData, VariantData
from opensmi_ui.opc_session.session import get_module_logger

logger = get_module_logger("opc_model.entity.variable")


class VariableEntityData(FeatureNodeEntityData):
    name: str
    description: LocalizedTextData

    data_type: str

    value: VariantData | None
    last_updated_at: datetime | None

    rank: int

    is_writable: bool

    modifiers: list[Any]


class VariableEntity(FeatureNodeEntity):
    content: VariableEntityData

    def __init__(self, opc_node: OPCNode):
        desc = opc_node.attributes.get("Description", "")

        data_type_node = opc_node.attributes.get("DataType", None)

        if data_type_node is not None and isinstance(data_type_node, ua.NodeId):
            try:
                data_type = str(ua.object_ids.ObjectIdNames[data_type_node.Identifier])
            except KeyError:
                data_type = str(data_type_node)
        else:
            data_type = "unknown"

        # check writeability
        is_writable = False
        access_level = opc_node.attributes.get("UserAccessLevel", None)
        if access_level is not None:
            access_bits = ua.AccessLevel.parse_bitfield(access_level)
            is_writable = ua.AccessLevel.CurrentWrite in access_bits

        # try to create modifiers
        modifiers: list[VariableModifierData] = []
        for property_key, property in opc_node.properties.items():
            match property_key:
                case "EngineeringUnits":
                    try:
                        unit_modifier = UnitModifier(property)
                        modifiers.append(unit_modifier.get_data())
                    except Exception:
                        logger.exception("failed to create UnitModifier for property")
                        continue
                case "EURange":
                    try:
                        range_modifier = RangeModifier(property)
                        modifiers.append(range_modifier.get_data())
                    except Exception:
                        logger.exception("failed to create RangeModifier for property")
                        continue

        content = VariableEntityData(
            name=opc_node.browse_name.Name,
            description=LocalizedTextData.from_ua(desc),
            data_type=(data_type),
            is_writable=is_writable,
            last_updated_at=datetime.now().astimezone(),
            modifiers=modifiers,
            rank=0,
            value=None,
        )

        self.content = content

    def update_value(self, new_value: VariantData):
        self.content.value = new_value

    def get_data(self) -> FeatureNodeEntityData:
        return self.content
