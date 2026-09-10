<script setup lang="ts">
import { Position, Handle } from "@vue-flow/core";
import type { NodeProps } from "@vue-flow/core";
import { computed } from "vue";

const props = defineProps<{
  node: NodeProps;
  state: string;
}>();

const isActive = computed(() => {
  return props.node.data.label == props.state;
});
</script>

<template>
  <div class="skill-state-node halting-node" :class="{ 'is-active': isActive }">
    <div>{{ node.data.label }}</div>
    <Handle type="target" :position="Position.Right" />
    <Handle type="source" :position="Position.Bottom" />
  </div>
</template>


<style scoped>
.halting-node {
  @apply bg-blue-100 text-blue-800 border-dashed;
}
</style>