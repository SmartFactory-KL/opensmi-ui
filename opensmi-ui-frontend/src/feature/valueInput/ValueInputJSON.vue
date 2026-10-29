<script setup lang="ts">
import type { VariableModifier } from "@/types/NodeFeatureTypes";
import { computed, ref, watch } from "vue";

const props = defineProps<{modifiers?: VariableModifier[]}>()

// Fallback for types without a dedicated editor (ExtensionObject, DataValue,
// Variant, DiagnosticInfo). Edits the encoded value as JSON.
const model = defineModel<unknown>({ required: true });

const draft = ref(JSON.stringify(model.value ?? null, null, 2));
const error = ref<string | null>(null);
const rows = computed(() => Math.min(12, Math.max(2, draft.value.split("\n").length)));

function onInput(event: Event) {
    draft.value = (event.target as HTMLTextAreaElement).value;
    try {
        model.value = JSON.parse(draft.value);
        error.value = null;
    } catch (e) {
        error.value = (e as Error).message; // keep the last valid value
    }
}

watch(model, (value) => {
    try {
        if (JSON.stringify(JSON.parse(draft.value)) === JSON.stringify(value ?? null)) return;
    } catch {
        // draft is not valid JSON, replace it below
    }
    draft.value = JSON.stringify(value ?? null, null, 2);
    error.value = null;
});
</script>

<template>
    <div class="flex flex-col gap-1">
        <textarea
            :value="draft"
            :rows="rows"
            spellcheck="false"
            :aria-invalid="error !== null"
            class="min-w-48 border px-1 text-xs font-mono"
            :class="error ? 'border-red-500' : 'border-stone-300'"
            @input="onInput"
        ></textarea>
        <span v-if="error" class="text-xs text-red-600">{{ error }}</span>
    </div>
</template>
