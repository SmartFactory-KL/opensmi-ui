<script setup lang="ts">
import { computed } from "vue";

import DefaultMachineLock from "./lock/DefaultMachineLock.vue";
import DisabledMachineLock from "./lock/DisabledMachineLock.vue";

const props = defineProps<{
  lockingModule: LockingModuleDto;
  serverUserName: string;
  enableTitle?: boolean;
}>();

const lockComponent = computed(() => {
  if (props.lockingModule.isEnabled == true) {
    return DefaultMachineLock;
  }

  return DisabledMachineLock;
});
</script>

<template>
  <component
    :is="lockComponent"
    :lockingModule="lockingModule"
    :server-user-name="serverUserName"
    :enable-title="enableTitle"
  ></component>
</template>
