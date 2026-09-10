<script lang="ts" setup>
import { VueFlow } from "@vue-flow/core";
import { ref } from "vue";
import { Node, Edge, MarkerType } from "@vue-flow/core";

import NodeHalted from "./NodeHalted.vue";
import NodeHalting from "./NodeHalting.vue";
import NodeCompleted from "./NodeCompleted.vue";
import NodeCompleting from "./NodeCompleting.vue";
import NodeReady from "./NodeReady.vue";
import NodeResetting from "./NodeResetting.vue";
import NodeRunning from "./NodeRunning.vue";
import NodeStarting from "./NodeStarting.vue";
import NodeSuspended from "./NodeSuspended.vue";
import NodeSuspending from "./NodeSuspending.vue";

defineProps<{
  state: string;
}>();

const colStep = 150;
const rowStep = 100;
const padLeft = 20;
const padTop = 20;

const nodes = ref<Node[]>([
  {
    id: "ready",
    type: "ready",
    position: { x: padLeft + 2 * colStep, y: padTop + 1 * rowStep },
    data: { label: "Ready" },
  },

  {
    id: "starting",
    type: "starting",
    position: { x: padLeft + 3 * colStep, y: padTop + 1 * rowStep },
    data: { label: "Starting" },
  },

  {
    id: "running",
    type: "running",
    position: { x: padLeft + 3 * colStep, y: padTop + 0 * rowStep },
    data: { label: "Running" },
  },

  {
    id: "resetting",
    type: "resetting",
    position: { x: padLeft + 1 * colStep, y: padTop + 1 * rowStep },
    data: { label: "Resetting" },
  },

  {
    id: "halting",
    type: "halting",
    position: { x: padLeft + 0 * colStep, y: padTop + 0 * rowStep },
    data: { label: "Halting" },
  },

  {
    id: "halted",
    type: "halted",
    position: { x: padLeft + 0 * colStep, y: padTop + 1 * rowStep },
    data: { label: "Halted" },
  },

  {
    id: "suspended",
    type: "suspended",
    position: { x: padLeft + 20 + 4 * colStep, y: padTop + 1 * rowStep },
    data: { label: "Suspended" },
  },
  {
    id: "suspending",
    type: "suspending",
    position: { x: padLeft + 20 + 4 * colStep, y: padTop + 0 * rowStep },
    data: { label: "Suspending" },
  },
]);

// these are our edges
const edges = ref<Edge[]>([
  {
    id: "halted->resetting",
    label: "Reset",
    source: "halted",
    target: "resetting",
    markerEnd: MarkerType.ArrowClosed,
  },
  {
    id: "halting->halted",
    source: "halting",
    target: "halted",
    markerEnd: MarkerType.ArrowClosed,
  },
  {
    id: "resetting->ready",
    label: "SC",
    source: "resetting",
    target: "ready",
    markerEnd: MarkerType.ArrowClosed,
  },
  {
    id: "ready->starting",
    label: "Start",
    source: "ready",
    target: "starting",
    markerEnd: MarkerType.ArrowClosed,
  },
  {
    id: "starting->running",
    label: "Internal SC",
    source: "starting",
    target: "running",
    markerEnd: MarkerType.ArrowClosed,
  },
  {
    id: "running->resetting",
    label: "Reset",
    source: "running",
    target: "resetting",
    targetHandle: "handle-resetting-top",
    markerEnd: MarkerType.ArrowClosed,
  },
  {
    id: "running->halting",
    label: "Halt",
    source: "running",
    target: "halting",
    markerEnd: MarkerType.ArrowClosed,
  },
  {
    id: "running->suspend",
    label: "Suspend",
    source: "running",
    target: "suspending",
    sourceHandle: "handle-running-right",
    markerEnd: MarkerType.ArrowClosed,
  },
  {
    id: "suspending->suspended",
    label: "SC",
    source: "suspending",
    target: "suspended",
    markerEnd: MarkerType.ArrowClosed,
  },
  {
    id: "suspended->starting",
    label: "Start",
    source: "suspended",
    target: "starting",
    targetHandle: "handle-starting-right",
    markerEnd: MarkerType.ArrowClosed,
  },
]);
</script>

<template>
  <VueFlow
    :nodes="nodes"
    :edges="edges"
    :fit-view-on-init="true"
    :nodes-draggable="false"
    :nodes-focusable="false"
    :nodes-connectable="false"
    :edges-updatable="false"
    :edges-focusable="false"
    :elements-selectable="false"
    :pan-on-drag="false"
    :zoom-on-double-click="false"
    :zoom-on-scroll="false"
    :zoom-on-pinch="false"
    class="state-machine-display"
  >
    <template #node-halted="prop">
      <NodeHalted :node="prop" :state="state"></NodeHalted>
    </template>
    <template #node-halting="prop">
      <NodeHalting :node="prop" :state="state" />
    </template>
    <template #node-completed="prop">
      <NodeCompleted :node="prop" :state="state" />
    </template>
    <template #node-resetting="prop">
      <NodeResetting :node="prop" :state="state" />
    </template>
    <template #node-completing="prop">
      <NodeCompleting :node="prop" :state="state" />
    </template>
    <template #node-ready="prop">
      <NodeReady :node="prop" :state="state" />
    </template>
    <template #node-running="prop">
      <NodeRunning :node="prop" :state="state" />
    </template>
    <template #node-starting="prop">
      <NodeStarting :node="prop" :state="state" />
    </template>
    <template #node-suspending="prop">
      <NodeSuspending :node="prop" :state="state" />
    </template>
    <template #node-suspended="prop">
      <NodeSuspended :node="prop" :state="state" />
    </template>
  </VueFlow>
</template>

<style>
.skill-state-node {
  @apply text-sm p-2 border border-gray-400 bg-slate-200 rounded-lg text-slate-600 text-center;
  cursor: default;
  width: 6rem;
}

.is-active {
  @apply font-bold underline border-slate-800;
}

.vue-flow__handle {
  opacity: 0.4;
}

.vue-flow__edge {
  cursor: default;
}
</style>
