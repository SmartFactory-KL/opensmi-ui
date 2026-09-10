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
  <div class="skill-state-node running-node" :class="{ 'is-active': isActive }">
    <div>{{ node.data.label }}</div>
    <Handle type="target" :position="Position.Bottom" />
    <Handle id="handle-running-left" type="source" :position="Position.Left" />
    <Handle
      id="handle-running-right"
      type="source"
      :position="Position.Right"
    />
  </div>
</template>


<style scoped>
.running-node {
  @apply bg-lime-100 text-lime-800;
}
</style>