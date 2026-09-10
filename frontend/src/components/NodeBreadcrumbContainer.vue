<script lang="ts" setup>
import NodeBreadcrumbItem from "./NodeBreadcrumbItem.vue";

defineProps<{
  parentNodeIdList: string[];
}>();
</script>

<template>
  <div class="flex flex-row gap-x-2">
    <div v-for="(parentNodeId, idx) in parentNodeIdList" :key="idx" class="flex flex-row justify-start items-center gap-x-1">
      <NodeBreadcrumbItem  :nodeId="parentNodeId"></NodeBreadcrumbItem>
      <i class="fa fa-caret-right"></i>
    </div>
    <i class="fa fa-circle text-slate-500"></i>
  </div>
</template>
