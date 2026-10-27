<script setup lang="ts">
defineProps<{
    value: string;
}>();
</script>

<template>
    <span v-if="value === ''" class="text-xs italic text-slate-400">
        (empty)
    </span>
    <span v-else class="whitespace-pre-wrap wrap-break-word">{{ value }}</span>
</template>
