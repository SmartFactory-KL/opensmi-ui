from typing import TYPE_CHECKING, Dict
import uuid

if TYPE_CHECKING:
    from opc_client.method_module import MethodModule
    from opc_client.component_module import ComponentModule
    from opc_client.machine_module import MachineModule
    from opc_client.skill_module import SkillModule
    from opc_client.remote_variable_module import RemoteVariableModule


class ReferenceStore:
    skill_map: Dict[uuid.UUID, "SkillModule"] = {}
    component_map: Dict[uuid.UUID, "ComponentModule"] = {}
    machine_map: Dict[uuid.UUID, "MachineModule"] = {}
    remote_variable_map: Dict[uuid.UUID, "RemoteVariableModule"] = {}
    method_map: Dict[uuid.UUID, "MethodModule"] = {}

    def clear(self):
        self.skill_map.clear()
        self.component_map.clear()
        self.machine_map.clear()
        self.remote_variable_map.clear()
        self.method_map.clear()

    def add_skill(self, skill_reference: "SkillModule"):
        self.skill_map[skill_reference.entity_id] = skill_reference

    def add_component(self, component_reference: "ComponentModule"):
        self.component_map[component_reference.entity_id] = component_reference

    def add_machine(self, machine_reference: "MachineModule"):
        self.machine_map[machine_reference.entity_id] = machine_reference

    def add_remote_variable(self, remote_variable_reference: "RemoteVariableModule"):
        self.remote_variable_map[remote_variable_reference.entity_id] = (
            remote_variable_reference
        )

    def add_method(self, method_reference: "MethodModule"):
        self.method_map[method_reference.entity_id] = method_reference

    def get_skill(self, skill_entity_id: uuid.UUID):
        return self.skill_map.get(skill_entity_id, None)

    def get_component(self, component_entity_id: uuid.UUID):
        return self.component_map.get(component_entity_id, None)

    def get_machine(self, machine_entity_id: uuid.UUID):
        return self.machine_map.get(machine_entity_id, None)

    def get_remote_variable(self, remote_variable_entity_id: uuid.UUID):
        return self.remote_variable_map.get(remote_variable_entity_id, None)

    def get_method(self, method_entity_id: uuid.UUID):
        return self.method_map.get(method_entity_id, None)


class NodeEntityStore:
    node_id_entity_id_map: Dict[str, uuid.UUID] = {}

    def clear(self):
        self.node_id_entity_id_map.clear()

    def add_node_entity_reference(self, node_id: str, entity_id: uuid.UUID):
        self.node_id_entity_id_map[node_id] = entity_id

    def get_entity_id_for_node_id(self, node_id: str):
        return self.node_id_entity_id_map.get(node_id, None)
