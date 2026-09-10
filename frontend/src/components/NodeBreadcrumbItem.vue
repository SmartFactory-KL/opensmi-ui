<script lang="ts" setup>
import { computed } from "vue";
import { useMachineStore } from "../stores/MachineStore";

const props = defineProps<{
  nodeId: string;
}>();

const machineStore = useMachineStore();

const targetEntityLink = computed((): string => {
  if (machineStore.nodeIdComponentMap.has(props.nodeId)) {
    return (
      "/component/" +
        machineStore.nodeIdComponentMap.get(props.nodeId)?.entityId || ""
    );
  }

  if (machineStore.nodeIdMethodMap.has(props.nodeId)) {
    return (
      "/method/" +
        machineStore.nodeIdComponentMap.get(props.nodeId)?.entityId || ""
    );
  }

  if (machineStore.nodeIdSkillMap.has(props.nodeId)) {
    return (
      "/skill/" + machineStore.nodeIdComponentMap.get(props.nodeId)?.entityId ||
      ""
    );
  }

  return "";
});

const label = computed(() => {
  if (!props.nodeId?.length) {
    return "-";
  }

  return props.nodeId.split("=").pop()?.split(".").pop() ?? "-";
});
</script>

<template>
  <div class="bg-slate-500 text-slate-50 h-4 px-2 leading-4 font-[400] text-xs">
    <RouterLink :to="targetEntityLink" v-if="targetEntityLink.length > 0">
      {{ label }}
    </RouterLink>
    <span v-else>{{ label }}</span>
  </div>
</template>
