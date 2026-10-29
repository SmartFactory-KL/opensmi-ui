<script setup lang="ts">
import type { VariableModifier } from "@/types/NodeFeatureTypes";
import { computed, ref, watch } from "vue";

const props = defineProps<{ modifiers?: VariableModifier[] }>();

// NaN and +/-Infinity are strings on the wire, finite values are numbers.
const model = defineModel<number | string | null>({ required: true });

const SPECIAL = ["NaN", "Infinity", "-Infinity"];
const HINT = "Enter a number, NaN, Infinity or -Infinity";

type Parsed = { value: number | string } | { error: string };

function parse(text: string): Parsed {
    const t = text.trim();
    if (SPECIAL.includes(t)) return { value: t };
    if (t === "") return { error: HINT };
    const n = Number(t);
    if (Number.isNaN(n)) return { error: HINT };
    // JSON.stringify would turn a real Infinity into null
    if (!Number.isFinite(n))
        return { error: "Too large, use Infinity or -Infinity" };
    return { value: n };
}

const draft = ref(model.value == null ? "" : String(model.value));
const parsed = computed(() => parse(draft.value));
const error = computed(() =>
    "error" in parsed.value ? parsed.value.error : null,
);

function onInput(event: Event) {
    draft.value = (event.target as HTMLInputElement).value;
    const result = parse(draft.value);
    if ("value" in result) model.value = result.value;
}

watch(model, (value) => {
    const result = parse(draft.value);
    if ("value" in result && result.value === value) return;
    draft.value = value == null ? "" : String(value);
});
</script>

<template>
    <input
        type="text"
        inputmode="decimal"
        :value="draft"
        :title="error ?? undefined"
        :aria-invalid="error !== null"
        class="min-w-10 min-h-6 border px-1 text-sm font-mono"
        :class="error ? 'border-red-500' : 'border-stone-300'"
        @input="onInput"
    />
</template>
