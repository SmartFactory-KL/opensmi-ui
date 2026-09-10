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
  <div class="skill-state-node resetting-node" :class="{ 'is-active': isActive }">
    <div>{{ node.data.label }}</div>
    <Handle id="handle-resetting-left" type="target" :position="Position.Left" />
    <Handle id="handle-resetting-top" type="target" :position="Position.Top" />
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<style>
.resetting-node {
  @apply  border-dashed;
}
</style>
