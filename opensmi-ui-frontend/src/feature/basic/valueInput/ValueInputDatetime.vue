<script setup lang="ts">
import type { VariableModifier } from "@/types/NodeFeatureTypes";
import { computed } from "vue";

const props = defineProps<{modifiers?: VariableModifier[]}>()

// The wire format is an ISO string in UTC. datetime-local has no time zone,
// so the field is shown and edited as UTC.
const model = defineModel<string | null>({ required: true });

const local = computed({
    get: () => {
        if (!model.value) return "";
        const date = new Date(model.value);
        return Number.isNaN(date.getTime()) ? "" : date.toISOString().slice(0, 23);
    },
    set: (text: string) => {
        if (!text) {
            model.value = null;
            return;
        }
        const date = new Date(`${text}Z`);
        if (!Number.isNaN(date.getTime())) model.value = date.toISOString();
    },
});
</script>

<template>
    <div class="flex flex-row items-center gap-1">
        <input
            type="datetime-local"
            step="0.001"
            v-model="local"
            class="min-h-6 border border-stone-300 px-1 text-sm"
        />
        <span class="text-xs text-stone-500">UTC</span>
    </div>
</template>
