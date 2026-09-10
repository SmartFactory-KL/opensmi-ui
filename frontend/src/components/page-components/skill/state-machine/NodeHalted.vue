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
  <div class="skill-state-node halted-node" :class="{ 'is-active': isActive }">
    <div>{{ node.data.label }}</div>
    <Handle type="target" :position="Position.Top" />
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<style scoped>
.halted-node {
  @apply bg-blue-100 text-blue-800;
}

</style>
