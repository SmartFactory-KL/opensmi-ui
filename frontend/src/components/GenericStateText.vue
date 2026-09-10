<script lang="ts" setup>
import { computed } from "vue";

const props = defineProps<{
  state: string | number;
}>();

const stateColor = computed(() => {
  switch (props.state) {
    case "Halted":
    case 11:
      return ["text-blue-200"];
    case "Ready":
    case 12:
      return ["text-green-500"];
    case "Running":
    case 13:
      return ["text-yellow-500", "animate-pulse"];
    case "Suspended":
    case 14:
      return ["text-gray-200"];
    case "Completed":
    case 15:
      return ["text-violet-400"];
    case "Starting":
    case 16:
      return ["text-yellow-500"];
    case "Halting":
    case 17:
      return ["text-yellow-500"];
    case "unknown":
      return ["text-pink-500"];
    default:
      return ["text-white"];
  }
});

const stateLabel = computed(() => {
  if(Number.isInteger(props.state)) {
    return stateLabelMap.get(props.state as number);
  } else {
    return props.state || "unknown";
  }  
});

const stateLabelMap = new Map<number, string>([
  [11, "Halted"],
  [12, "Ready"],
  [13, "Running"],
  [14, "Suspended"],
  [15, "Completed"],
  [16, "Starting"],
  [17, "Halting"],
]);
</script>

<template>
  <div class="module-state-display" :class="stateColor">
    {{ stateLabel }}
  </div>
</template>

<style scoped>
.module-state-display {
  @apply text-xs;
  border-radius: 1rem;
  width: max-content;
}
</style>
