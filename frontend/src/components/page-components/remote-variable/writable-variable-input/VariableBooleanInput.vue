<script lang="ts" setup>
defineProps<{
  remoteVariable: RemoteVariableDto;
  enableWrites: boolean;
}>();
</script>

<template>
  <input
    type="checkbox"
    v-model="remoteVariable.tempDataContent.value.value"
    class="px-2 scale-150"
    :disabled="!enableWrites"
  />
</template>
