<script setup lang="ts">
import type { VariantData, VariantTypeName } from "@/types/OPCTypes";
import ValueDisplay from "./ValueDisplay.vue"; // your dispatcher

defineProps<{
    type: VariantTypeName;
    value: unknown[]; // nested for multi-dimensional arrays
}>();

// Rebuilds a Variant for one element, so the dispatcher can pick the component.
// Nested lists (multi-dimensional arrays) recurse through ValueDisplayArray.
function asVariant(type: VariantTypeName, item: unknown): VariantData {
    return {
        type,
        isArray: Array.isArray(item),
        dimensions: null,
        value: item,
    } as VariantData;
}
</script>

<template>
    <span v-if="value.length === 0" class="text-xs italic text-slate-400">
        (empty array)
    </span>
    <ol
        v-else
        class="flex flex-col gap-0.5 border-l border-slate-200 pl-2 text-sm"
    >
        <li
            v-for="(item, index) in value"
            :key="index"
            class="flex items-baseline gap-2"
        >
            <span class="w-6 shrink-0 text-right text-xs text-slate-400">
                {{ index }}
            </span>
            <ValueDisplay :variable-value="asVariant(type, item)" />
        </li>
    </ol>
</template>
