<script lang="ts" setup>
import { computed } from "vue";

const props = defineProps<{
  state: string | number | null;
  minimal?: boolean;
}>();

const stateColor = computed(() => {
  switch (props.state) {
    case "Halted":
    case 11:
      return ["text-blue-200", "bg-blue-500"];
    case "Ready":
    case 12:
      return ["text-gray-700", "bg-green-500"];
    case "Running":
    case 13:
      return [
        "text-gray-700",
        "bg-green-500",
        "animate-pulse",
        "border-4",
        "border-lime-600",
      ];
    case "Suspended":
    case 14:
      return ["text-gray-700", "bg-pink-500"];
    case "Completed":
    case 15:
      return ["text-violet-200", "bg-violet-500"];
    case "Starting":
    case 16:
      return ["text-yellow-200", "bg-yellow-500"];
    case "Halting":
    case 17:
      return ["text-yellow-200", "bg-yellow-500"];
    case "unknown":
      return ["text-pink-200", "bg-pink-500"];
    default:
      return ["text-gray-400", "bg-gray-300"];
  }
});

const stateLabel = computed(() => {
  if (Number.isInteger(props.state)) {
    return stateLabelMap.get(props.state as number);
  } else {
    return props.state || "no state";
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

const stateSymbol = computed(() => {
  switch (stateLabel.value) {
    case "Halted":
      return "fa-power-off";
    case "Ready":
      return "fa-play";
    case "Running":
      return "fa-circle-dot";
    case "Suspended":
      return "fa-pause";
    case "Completed":
      return "fa-check";
    case "Starting":
      return "fa-play";
    case "Halting":
      return "fa-power-off";
    default:
      break;
  }
});
</script>

<template>
  <div
    class="module-state-display"
    :title="(stateLabel as string)"
    :class="[
      stateColor,
      {
        'module-state-display': !minimal,
        'module-state-minimal': minimal,
      },
    ]"
  >
    <i class="fa fa-solid opacity-80" :class="[stateSymbol]"></i>
    <span v-show="!minimal">{{ stateLabel }}</span>
  </div>
</template>

<style scoped>
.module-state-display {
  @apply text-xs flex flex-row justify-center items-center;
  border-radius: 1rem;
  height: 1.6rem;
  width: 7rem;
  column-gap: 0.4rem;
  text-align: center;
}

.module-state-minimal {
  @apply text-xs flex flex-row justify-center items-center;
  border-radius: 50%;
  width: 1.3rem;
  height: 1.3rem;
  text-align: center;
}
</style>
