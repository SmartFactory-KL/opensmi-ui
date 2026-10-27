<script setup lang="ts">
import { computed } from "vue";
import type { ExpandedNodeIdData, NodeIdData } from "@/types/OPCTypes";

const props = defineProps<{
    value: NodeIdData | ExpandedNodeIdData;
}>();

const PREFIX: Record<string, string> = {
    TwoByte: "i",
    FourByte: "i",
    Numeric: "i",
    String: "s",
    Guid: "g",
    ByteString: "b",
};

function format(id: NodeIdData): string {
    const ns = id.namespaceIndex ? `ns=${id.namespaceIndex};` : "";
    return `${ns}${PREFIX[id.identifierType] ?? "?"}=${id.identifier}`;
}

const text = computed(() => {
    if ("nodeId" in props.value) {
        const { nodeId, namespaceUri, serverIndex } = props.value;
        const server = serverIndex ? `svr=${serverIndex};` : "";
        const nsu = namespaceUri ? `nsu=${namespaceUri};` : "";
        return server + nsu + format(nodeId);
    }
    return format(props.value);
});
</script>

<template>
    <span class="font-mono text-xs break-all" :title="text">{{ text }}</span>
</template>
