<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
    defineProps<{ kind?: "string" | "guid" | "base64" }>(),
    {
        kind: "string",
    },
);
const model = defineModel<string | null>({ required: true });

const GUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const BASE64 =
    /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/;

// Only marks the field, the value is still written so that nothing typed is lost.
const error = computed(() => {
    const value = model.value ?? "";
    if (props.kind === "guid" && !GUID.test(value)) {
        return "Expected a GUID like 00000000-0000-0000-0000-000000000000";
    }
    if (props.kind === "base64" && !BASE64.test(value)) {
        return "Expected Base64";
    }
    return null;
});
</script>

<template>
    <input
        type="text"
        v-model="model"
        :title="error ?? undefined"
        :aria-invalid="error !== null"
        class="min-w-10 min-h-6 border px-1 text-sm"
        :class="[
            error ? 'border-red-500' : 'border-stone-300',
            props.kind !== 'string' && 'font-mono',
        ]"
    />
</template>
