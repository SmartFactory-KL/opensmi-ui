<script setup lang="ts">
import { computed } from "vue";
import type { LocalizedTextData, QualifiedNameData } from "@/types/OPCTypes";

const props = defineProps<{
    value: LocalizedTextData | QualifiedNameData;
}>();

const isLocalized = computed(() => "text" in props.value);

const text = computed(() => {
    const v = props.value;
    if ("text" in v) return v.text ?? "";
    return v.namespaceIndex ? `${v.namespaceIndex}:${v.name}` : v.name;
});

const locale = computed(() =>
    "locale" in props.value ? props.value.locale : null,
);
</script>

<template>
    <span class="inline-flex flex-wrap items-baseline gap-x-2">
        <span :class="isLocalized ? '' : 'font-mono text-sm'">{{ text }}</span>
        <span
            v-if="locale"
            class="rounded-full bg-slate-100 px-1.5 text-xs text-slate-500"
        >
            {{ locale }}
        </span>
    </span>
</template>
