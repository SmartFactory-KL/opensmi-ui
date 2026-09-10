<script setup lang="ts">
import RemoteVariableDisplay from "./RemoteVariableDisplay.vue";

defineProps<{
  label: string;
  remoteVariableList: RemoteVariableDto[];
}>();
</script>

<template>
  <div class="remote-variable-list">
    <div class="list-title text-lg text-primary">
      {{ label }}
    </div>
    <hr class="border-primary">
    <div class="list flex flex-col gap-y-4">
      <RemoteVariableDisplay
        v-for="remoteVariable of remoteVariableList"
        :remote-variable="remoteVariable"
      ></RemoteVariableDisplay>
    </div>
  </div>
</template>

<style scoped>
.remote-variable-list {
  @apply p-4 border border-primary;
}
</style>
