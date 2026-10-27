<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
    value: unknown;
}>();

const json = computed(() => JSON.stringify(props.value, null, 2) ?? "");
</script>

<template>
    <pre
        class="max-w-full overflow-x-auto rounded bg-slate-50 p-1.5 font-mono text-xs"
        >{{ json }}</pre
    >
</template>
