<script lang="ts" setup>
import { useMachineStore } from "../../../stores/MachineStore";
import { useServerStore } from "../../../stores/ServerStore";
import { usePageStore } from "../../../stores/PageStore";
import MachineLockDisplay from "../../machine/MachineLockDisplay.vue";
import ComponentTreeLink from "./ComponentTreeLink.vue";
import SkillLink from "../skill/SkillLink.vue";
import MethodLink from "../method/MethodLink.vue";

const props = defineProps<{
  machine: MachineDto;
}>();

const serverStore = useServerStore();
const machineStore = useMachineStore();
const pageStore = usePageStore();

function lockRequest() {
  machineStore.requestLockToggleForMachine(props.machine.entityId);
}
</script>

<template>
  <div class="machine-nav-item">
    <div class="machine-information">
      <div class="machine-title">
        {{ machine.name }}
        <div class="machine-lock">
          <MachineLockDisplay
            :lockingModule="machine.lockingModule"
            :server-user-name="serverStore.connectionData.username"
            @lock-request="lockRequest"
          ></MachineLockDisplay>
        </div>
      </div>
      <div class="machine-node-id">
        <span v-show="pageStore.showFlags.nodeIds">
          {{ machine.nodeId }}
        </span>
      </div>
      <div class="machine-node-id">
        {{ machine.currentState }}
      </div>

      <div class="text-xs text-gray-500" v-show="pageStore.showFlags.entityIds">
        {{ machine.entityId }}
      </div>

      <RouterLink
        class="machine-link mt-2"
        :to="'/machine/' + machine.entityId"
      >
        <div class="flex flex-row justify-start items-center gap-x-3">
          <i class="fa-solid fa-house-fire"></i>
          <span>Machine</span>
          <i class="fa-solid fa-angle-right"></i>
        </div>
      </RouterLink>
    </div>

    <div class="machine-link-list">
      <div class="text-pink-200">Components</div>
      <ComponentTreeLink
        :component="component"
        v-for="component of machine.components"
      >
      </ComponentTreeLink>
      <div class="text-pink-200">Skills</div>

      <SkillLink
        :skill="skill"
        v-for="skill of machine.skillSet"
        class="my-2"
      ></SkillLink>

      <MethodLink
        :method="method"
        v-for="method of machine.methods"
        class="my-2"
      ></MethodLink>
    </div>
  </div>
</template>

<style scoped>
.machine-nav-item {
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: stretch;
}

.machine-information {
  @apply bg-primary p-4;
  position: sticky;
  top: 0;
  z-index: 10;
}

.machine-title {
  @apply text-lg font-bold;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.machine-node-id {
  @apply text-sm text-gray-400;
}

.machine-link-list {
  @apply border-l-2 border-l-primary border-b-2 border-b-primary p-2;
}

.machine-link {
  display: flex;
  flex-direction: row;
  column-gap: 0.5rem;
  justify-content: flex-start;
  align-items: center;
  cursor: pointer;
}

.machine-link.router-link-active {
  @apply font-bold;
}

.machine-link:hover {
  @apply text-secondary translate-x-1;
}
</style>
