<script setup lang="ts">
import type { VariantData } from "@/types/OPCTypes";
import { computed } from "vue";

import ValueInputText from "./ValueInputText.vue";

const props = defineProps<{
    variableValue: VariantData | null;
}>();

const inputComponent = computed(() => {
    if (props.variableValue === null) {
        return ValueInputText;
    }

    switch (props.variableValue.type) {
        case "Null":
        case "Boolean":
        case "SByte":
        case "Byte":
        case "ByteString":
        case "Int16":
        case "UInt16":
        case "Int32":
        case "UInt32":
        case "Int64":
        case "UInt64":
        case "Float":
        case "Double":
        case "String":
        case "XmlElement":
        case "DateTime":
        case "Guid":
        case "NodeId":
        case "ExpandedNodeId":
        case "StatusCode":
        case "QualifiedName":
        case "LocalizedText":
        case "ExtensionObject":
        case "DataValue":
        case "Variant":
        case "DiagnosticInfo":
        default:
            return ValueInputText;
    }
});
</script>

<template>
    <!-- <ValueDisplayNull v-if="variableValue === null" :value="null" />
    <ValueDisplayArray
        v-else-if="variableValue.isArray"
        :type="variableValue.type"
        :value="variableValue.value"
    />
    <!-- null scalars (e.g. an empty String) are shown as "null" -->
    <!-- <ValueDisplayNull v-else-if="variableValue.value === null" :value="null" /> -->
    <!-- -->
    <component :is="inputComponent" :value="variableValue" />
</template>
