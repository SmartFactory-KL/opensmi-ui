<script setup lang="ts">
import type { ExpandedNodeIdData } from "@/types/OPCTypes";
import ValueInputNodeId from "./ValueInputNodeId.vue";

const model = defineModel<ExpandedNodeIdData>({ required: true });

function patch(change: Partial<ExpandedNodeIdData>) {
    model.value = { ...model.value, ...change };
}

function setUri(event: Event) {
    const text = (event.target as HTMLInputElement).value;
    patch({ namespaceUri: text === "" ? null : text });
}

function setServerIndex(event: Event) {
    const n = Number.parseInt((event.target as HTMLInputElement).value, 10);
    if (Number.isInteger(n) && n >= 0) patch({ serverIndex: n });
}
</script>

<template>
    <div class="flex flex-col gap-1">
        <ValueInputNodeId
            :model-value="model.nodeId"
            @update:model-value="patch({ nodeId: $event })"
        />
        <div class="flex flex-row items-center gap-1">
            <input
                type="text"
                placeholder="Namespace URI"
                :value="model.namespaceUri ?? ''"
                class="min-w-20 min-h-6 border border-stone-300 px-1 text-sm"
                @input="setUri"
            />
            <input
                type="number"
                min="0"
                title="Server index"
                :value="model.serverIndex"
                class="w-14 min-h-6 border border-stone-300 px-1 text-sm"
                @input="setServerIndex"
            />
        </div>
    </div>
</template>
