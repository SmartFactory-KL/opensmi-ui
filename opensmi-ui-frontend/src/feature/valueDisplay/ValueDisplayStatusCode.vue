<script setup lang="ts">
import { computed } from "vue";
import type { StatusCodeData } from "@/types/OPCTypes";

const props = defineProps<{
    value: StatusCodeData;
}>();

const SEVERITY_CLASSES = {
    good: "bg-emerald-50 text-emerald-700 border-emerald-200",
    uncertain: "bg-amber-50 text-amber-700 border-amber-200",
    bad: "bg-red-50 text-red-700 border-red-200",
} as const;

const hex = computed(
    () =>
        "0x" +
        (props.value.code >>> 0).toString(16).toUpperCase().padStart(8, "0"),
);
</script>

<template>
    <span
        class="inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs"
        :class="SEVERITY_CLASSES[value.severity]"
        :title="hex"
    >
        {{ value.name ?? hex }}
    </span>
</template>
