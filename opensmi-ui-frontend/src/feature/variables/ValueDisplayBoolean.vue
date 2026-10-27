<script setup lang="ts">
defineProps<{
    value: boolean;
}>();
</script>

<template>
    <span class="inline-flex items-center gap-1.5">
        <span
            class="size-2 rounded-full"
            :class="value ? 'bg-emerald-500' : 'bg-slate-300'"
        />
        {{ value ? "True" : "False" }}
    </span>
</template>
