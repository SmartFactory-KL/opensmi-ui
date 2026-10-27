<script setup lang="ts">
defineProps<{
    value: string;
}>();
</script>

<template>
    <span class="font-mono text-xs break-all">{{ value }}</span>
</template>
