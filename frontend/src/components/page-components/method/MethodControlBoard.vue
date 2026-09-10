<script setup lang="ts">
import { computed } from "vue";

import { useServerStore } from "../../../stores/ServerStore";
import { useMachineStore } from "../../../stores/MachineStore";
import { GenericActionDto } from "../../../types/ActionTypes";
import { usePinGuardStore } from "../../../stores/PinStore";

const machineStore = useMachineStore();
const serverStore = useServerStore();
const pinGuardStore = usePinGuardStore();

const props = defineProps<{
  method: MethodDto;
  showAsTiny: boolean;
}>();

function createMethodControlAction() {
  const methodAction: GenericActionDto = {
    entityId: props.method.entityId,
    entityType: "Method",
    actionType: "MethodCall",
    actionContent: null,
  };

  machineStore.requestMethodAction(methodAction);
}

const isMachineOfMethodLockedByUs = computed(() => {
  if (pinGuardStore.isLocked) {
    return false;
  }

  const machineForMethod = machineStore.entityToParentMachineMap.get(
    props.method.entityId
  );

  if (!machineForMethod) {
    return false;
  }

  if (!machineForMethod.lockingModule.isLocked) {
    return false;
  }

  if (
    machineForMethod.lockingModule.lockingUser !=
    serverStore.connectionData.username
  ) {
    return false;
  }

  return true;
});

const labelColor = computed(() => {
  if (isMachineOfMethodLockedByUs.value == false) {
    return "text-gray-400";
  }
  return "text-emerald-600";
});

const bgColor = computed(() => {
  if (isMachineOfMethodLockedByUs.value == false) {
    return "text-gray-400";
  }
  return "bg-emerald-200";
});
</script>

<template>
  <div
    class="skill-control-board"
    :class="[{ inactive: !isMachineOfMethodLockedByUs, tiny: showAsTiny }]"
  >
    <div class="control-knob-list">
      <button
        class="control-knob"
        type="button"
        @click="createMethodControlAction"
        :disabled="!isMachineOfMethodLockedByUs"
        :class="[bgColor]"
      >
        <i class="fa-solid fa-meteor" :class="[labelColor]"></i>
        <div class="text-sm" :class="[labelColor]">Call</div>
      </button>
    </div>
    <div v-show="!showAsTiny">
      <span
        class="text-red-400 flex flex-row justify-center items-center text-xs pt-2"
        v-show="!isMachineOfMethodLockedByUs"
      >
        Either the machine is not locked or the PinGuard is locked.
      </span>
    </div>
  </div>
</template>

<style scoped>
.skill-control-board {
  @apply border-2 border-secondary p-4;
}

.skill-control-board.tiny {
  @apply border-0 p-0;
}

.skill-control-board.inactive {
  @apply border border-gray-400;
}

.control-knob-list {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  column-gap: 1.5rem;
  align-items: center;
}

.tiny .control-knob-list {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  align-items: center;
  column-gap: 0;
}

.skill-control-knob {
  @apply border border-primary;
  width: 3rem;
  height: 3rem;
}

.control-knob {
  @apply border border-primary flex flex-col justify-center items-center;
  width: 4rem;
  height: 4rem;
}

.control-knob i {
  @apply text-3xl;
}

.control-knob.tiny i {
  @apply text-base;
}

.control-knob.tiny {
  width: 2rem;
  height: 2rem;
}

.control-knob:hover:enabled {
  scale: 1.05;
}

.control-knob:active:enabled {
  scale: 0.8;
}

.control-knob:disabled {
  @apply text-gray-400 cursor-not-allowed border-gray-400;
}
</style>
