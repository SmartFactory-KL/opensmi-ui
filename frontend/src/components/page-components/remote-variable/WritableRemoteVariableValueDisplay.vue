<script lang="ts" setup>
defineProps<{
  remoteVariable: RemoteVariableDto;
}>();
</script>

<template>
  <div class="flex flex-row justify-end basis-1/2 pr-4">
    <div class="mr-2" v-if="remoteVariable.remoteVariableType != 'Enum'">
      {{ remoteVariable.dataContent.value.value }}
    </div>
    <div v-else>
      {{ remoteVariable.remoteVariableAnnotation[remoteVariable.dataContent.value.value] }}
    </div>
    <div v-show="remoteVariable.unit?.length">| {{ remoteVariable.unit }}</div>
  </div>
</template>
