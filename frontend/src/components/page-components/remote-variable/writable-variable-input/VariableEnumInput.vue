<script lang="ts" setup>
defineProps<{
  remoteVariable: RemoteVariableDto;
  enableWrites: boolean;
}>();
</script>

<template>
  <select
    class="px-2"
    v-model="remoteVariable.tempDataContent.value.value"
    :disabled="!enableWrites"
  >
    <option :title="idx" v-for="[idx, option] in Object.entries(remoteVariable.remoteVariableAnnotation)" :value="idx">
      {{ option }}
    </option>
  </select>
</template>

<style scoped>
select {
  width: 100%;
}
</style>
