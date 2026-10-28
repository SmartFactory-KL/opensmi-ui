<script setup lang="ts">
import { computed, ref, watch } from "vue";

// SByte..UInt32 are numbers, Int64/UInt64 are decimal strings on the wire
// (they can exceed MAX_SAFE_INTEGER), so both are validated with BigInt.
const props = defineProps<{ type: string }>();
const model = defineModel<number | string | null>({ required: true });

const RANGES: Record<string, [bigint, bigint]> = {
    SByte: [-128n, 127n],
    Byte: [0n, 255n],
    Int16: [-32768n, 32767n],
    UInt16: [0n, 65535n],
    Int32: [-(2n ** 31n), 2n ** 31n - 1n],
    UInt32: [0n, 2n ** 32n - 1n],
    Int64: [-(2n ** 63n), 2n ** 63n - 1n],
    UInt64: [0n, 2n ** 64n - 1n],
};

type Parsed = { value: number | string } | { error: string };

function parse(text: string): Parsed {
    const t = text.trim();
    if (!/^[+-]?\d+$/.test(t)) return { error: "Enter a whole number" };
    const n = BigInt(t);
    const range = RANGES[props.type];
    if (range && (n < range[0] || n > range[1])) {
        return {
            error: `${props.type} must be between ${range[0]} and ${range[1]}`,
        };
    }
    const big = props.type === "Int64" || props.type === "UInt64";
    return { value: big ? n.toString() : Number(n) };
}

const draft = ref(model.value == null ? "" : String(model.value));
const parsed = computed(() => parse(draft.value));
const error = computed(() =>
    "error" in parsed.value ? parsed.value.error : null,
);

function onInput(event: Event) {
    draft.value = (event.target as HTMLInputElement).value;
    const result = parse(draft.value);
    if ("value" in result) model.value = result.value; // invalid text is not written
}

// follow outside changes (e.g. resetting the value) without clobbering "007" while typing
watch(model, (value) => {
    const result = parse(draft.value);
    if ("value" in result && result.value === value) return;
    draft.value = value == null ? "" : String(value);
});
</script>

<template>
    <input
        type="text"
        inputmode="numeric"
        :value="draft"
        :title="error ?? undefined"
        :aria-invalid="error !== null"
        class="min-w-10 min-h-6 border px-1 text-sm font-mono"
        :class="error ? 'border-red-500' : 'border-stone-300'"
        @input="onInput"
    />
</template>
