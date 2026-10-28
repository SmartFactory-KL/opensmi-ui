<script setup lang="ts">
import { computed } from "vue";
import { NUMERIC_NODE_ID_TYPES } from "./ValueInputUtils";
import type { NodeIdData } from "@/types/OPCTypes";

const model = defineModel<NodeIdData>({ required: true });

const BASE_TYPES = ["Numeric", "String", "Guid", "ByteString"];

const isNumeric = computed(() => NUMERIC_NODE_ID_TYPES.includes(model.value.identifierType));
const typeOptions = computed(() =>
    BASE_TYPES.includes(model.value.identifierType)
        ? BASE_TYPES
        : [model.value.identifierType, ...BASE_TYPES],
);

function patch(change: Partial<NodeIdData>) {
    model.value = { ...model.value, ...change };
}

function setNamespace(event: Event) {
    const n = Number.parseInt((event.target as HTMLInputElement).value, 10);
    if (Number.isInteger(n) && n >= 0) patch({ namespaceIndex: n });
}

function setType(event: Event) {
    const identifierType = (event.target as HTMLSelectElement).value;
    const identifier = NUMERIC_NODE_ID_TYPES.includes(identifierType)
        ? Number(model.value.identifier) || 0
        : String(model.value.identifier);
    patch({ identifierType, identifier });
}

function setIdentifier(event: Event) {
    const text = (event.target as HTMLInputElement).value;
    if (isNumeric.value) {
        const n = Number.parseInt(text, 10);
        if (Number.isInteger(n) && n >= 0) patch({ identifier: n });
    } else {
        patch({ identifier: text });
    }
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
        <select
            :value="model.identifierType"
            class="min-h-6 border border-stone-300 text-sm"
            @change="setType"
        >
            <option v-for="t in typeOptions" :key="t" :value="t">{{ t }}</option>
        </select>
        <input
            :type="isNumeric ? 'number' : 'text'"
            :min="isNumeric ? 0 : undefined"
            title="Identifier"
            :value="model.identifier"
            class="min-w-20 min-h-6 border border-stone-300 px-1 text-sm"
            @input="setIdentifier"
        />
    </div>
</template>
