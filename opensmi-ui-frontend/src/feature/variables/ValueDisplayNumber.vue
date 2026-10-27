<script setup lang="ts">
// Int64/UInt64 arrive as strings, Float/Double may be "NaN", "Infinity" or "-Infinity"
defineProps<{
    value: number | string;
}>();
</script>

<template>
    <span class="font-mono tabular-nums">
        {{ value }}
    </span>
</template>
