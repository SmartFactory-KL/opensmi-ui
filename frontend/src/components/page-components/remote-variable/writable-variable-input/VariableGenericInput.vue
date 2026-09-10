<script lang="ts" setup>
defineProps<{
  remoteVariable: RemoteVariableDto;
  enableWrites: boolean;
}>();
</script>

<template>
  <input
    type="text"
    v-model="remoteVariable.tempDataContent.value.value"
    class="px-2"
    :disabled="!enableWrites"
  />
</template>

<style scoped>
input {
  width: 100%;
}
</style>
