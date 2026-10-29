<script setup lang="ts">
import type { VariableModifier } from "@/types/NodeFeatureTypes";
import type { LocalizedTextData } from "@/types/OPCTypes";

const props = defineProps<{modifiers?: VariableModifier[]}>()
const model = defineModel<LocalizedTextData>({ required: true });

function setText(event: Event) {
    model.value = {
        ...model.value,
        text: (event.target as HTMLInputElement).value,
    };
}

function setLocale(event: Event) {
    const locale = (event.target as HTMLInputElement).value;
    model.value = { ...model.value, locale: locale === "" ? null : locale };
}
</script>

<template>
    <div class="flex flex-row items-center gap-1">
        <input
            type="text"
            placeholder="Text"
            :value="model.text ?? ''"
            class="min-w-20 min-h-6 border border-stone-300 px-1 text-sm"
            @input="setText"
        />
        <input
            type="text"
            placeholder="en"
            title="Locale"
            :value="model.locale ?? ''"
            class="w-14 min-h-6 border border-stone-300 px-1 text-sm"
            @input="setLocale"
        />
    </div>
</template>
