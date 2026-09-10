<script lang="ts" setup>
import { computed } from "vue";

const props = defineProps<{
  label: string;
  symbol: string;
  isActive: boolean;
  isTiny: boolean;
}>();

const emit = defineEmits(["control-click"]);

function handleClick() {
  if (props.isActive) {
    emit("control-click");
  }
}

const labelColor = computed(() => {
  if (props.isActive == false) {
    return "text-gray-400";
  }

  switch (props.label) {
    case "Reset":
      return "text-amber-600";
    case "Start":
      return "text-emerald-600";
    case "Halt":
      return "text-blue-600";
    case "Suspend":
      return "text-pink-600";
    default:
      return "text-white-400";
  }
});

const bgColor = computed(() => {
  if (props.isActive == false) {
    return "text-gray-400";
  }

  switch (props.label) {
    case "Reset":
      return "bg-amber-200";
    case "Start":
      return "bg-emerald-200";
    case "Halt":
      return "bg-blue-200";
    case "Suspend":
      return "bg-pink-200";
    default:
      return "bg-darkblue-800";
  }
});
</script>

<template>
  <button
    class="control-knob"
    type="button"
    @click="handleClick"
    :disabled="!isActive"
    :class="[bgColor, { tiny: isTiny }]"
  >
    <i
      class="fa-solid"
      :class="[symbol, labelColor]"
      v-show="isActive"
    ></i>
    <i
      class="fa-solid fa-ban text-gray-500 opacity-70"
      v-show="!isActive"
    ></i>
    <div class="text-sm" :class="[labelColor]" v-show="!isTiny">
      {{ label }}
    </div>
  </button>
</template>

<style scoped>
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

.control-knob:disabled {
  @apply text-gray-400 cursor-not-allowed border-gray-400;
}
</style>
