<script lang="ts" setup>
defineProps<{
  level: string;
  isActive: boolean;
}>();
</script>

<template>
  <div
    class="flex flex-row justify-center items-center gap-x-2 h-16 font-mono flex-grow cursor-pointer hover:bg-slate-600"
    :class="[isActive ? 'bg-slate-800' : 'bg-slate-500']"
  >
    <slot></slot>
  </div>
</template>
