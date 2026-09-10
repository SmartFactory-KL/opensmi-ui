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
  <div class="skill-state-node completed-node" :class="{ 'is-active': isActive }">
    <div>{{ node.data.label }}</div>
    <Handle
      id="handle-completed-left"
      type="source"
      :position="Position.Left"
    />
    <Handle
      id="handle-completed-bottom"
      type="source"
      :position="Position.Bottom"
    />
    <Handle type="target" :position="Position.Right" />
  </div>
</template>

<style scoped>
.completed-node {
  @apply bg-violet-100 text-violet-800;
}
</style>
