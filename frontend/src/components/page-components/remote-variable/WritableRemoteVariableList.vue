<script setup lang="ts">
import { computed } from "vue";
import WritableRemoteVariableDisplay from "./WritableRemoteVariableDisplay.vue";
import { useMachineStore } from "../../../stores/MachineStore";
import { useServerStore } from "../../../stores/ServerStore";
import { usePinGuardStore } from "../../../stores/PinStore";

const machineStore = useMachineStore();
const serverStore = useServerStore();
const pinGuardStore = usePinGuardStore();

const props = defineProps<{
  label: string;
  remoteVariableList: RemoteVariableDto[];
  parentEntityId: string;
}>();

const canExecuteParameterWrites = computed(() => {
  if (pinGuardStore.isLocked) {
    return false;
  }

  const machineForSkill = machineStore.entityToParentMachineMap.get(
    props.parentEntityId as string
  );

  if (!machineForSkill) {
    return false;
  }

  if (!machineForSkill.lockingModule.isLocked) {
    return false;
  }

  if (
    machineForSkill.lockingModule.lockingUser !=
    serverStore.connectionData.username
  ) {
    return false;
  }

  return true;
});

const emit = defineEmits<{
  (e: "bulk-write", remoteVariableList: RemoteVariableDto[]): void;
  (e: "single-write", remoteVariable: RemoteVariableDto): void;
}>();

function requestSingleWrite(remoteVariable: RemoteVariableDto) {
  emit("single-write", remoteVariable);
}
</script>

<template>
  <div class="remote-variable-list w-full">
    <div
      class="list-title text-lg text-gray-800 flex flex-row justify-between items-center"
    >
      {{ label }}
    </div>

    <div>
      <span
        class="text-red-400 flex flex-row justify-center items-center text-xs pt-2"
        v-show="!canExecuteParameterWrites && remoteVariableList.length > 0"
      >
        Either the machine is not locked or the PinGuard is locked.
      </span>
    </div>

    <div class="list flex flex-row flex-wrap gap-y-4 gap-x-4">
      <span v-show="remoteVariableList.length == 0" class="text-gray-400">
        - no parameters -
      </span>

      <WritableRemoteVariableDisplay
        v-for="remoteVariable of remoteVariableList"
        :remote-variable="remoteVariable"
        :enable-writes="canExecuteParameterWrites"
        @write-request="requestSingleWrite(remoteVariable)"
      ></WritableRemoteVariableDisplay>
    </div>
  </div>
</template>

<style scoped></style>
