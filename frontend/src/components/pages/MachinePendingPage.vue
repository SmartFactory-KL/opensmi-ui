<script lang="ts" setup>
import { useMachineStore } from "../../stores/MachineStore";
import LoadingIndicator from "../LoadingIndicator.vue";

const machineStore = useMachineStore();
</script>

<template>
  <div>
    <div v-if="!machineStore.refreshPending">
      <slot></slot>
    </div>
    <div v-else>
      <LoadingIndicator></LoadingIndicator>
    </div>
  </div>
</template>
