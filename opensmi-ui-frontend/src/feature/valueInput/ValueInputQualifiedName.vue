<script setup lang="ts">
import type { VariableModifier } from "@/types/NodeFeatureTypes";
import type { QualifiedNameData } from "@/types/OPCTypes";

const props = defineProps<{modifiers?: VariableModifier[]}>()
const model = defineModel<QualifiedNameData>({ required: true });

function setName(event: Event) {
    model.value = {
        ...model.value,
        name: (event.target as HTMLInputElement).value,
    };
}

function setNamespace(event: Event) {
    const n = Number.parseInt((event.target as HTMLInputElement).value, 10);
    if (Number.isInteger(n) && n >= 0)
        model.value = { ...model.value, namespaceIndex: n };
}
</script>

<template>
    <div class="flex flex-row items-center gap-1">
        <input
            type="number"
            min="0"
            title="Namespace index"
            :value="model.namespaceIndex"
            class="w-14 min-h-6 border border-stone-300 px-1 text-sm"
            @input="setNamespace"
        />
        <input
            type="text"
            placeholder="Name"
            :value="model.name"
            class="min-w-20 min-h-6 border border-stone-300 px-1 text-sm"
            @input="setName"
        />
    </div>
</template>
