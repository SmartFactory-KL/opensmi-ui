<script setup lang="ts">
import type { VariantData } from "@/types/OPCTypes";
import { computed } from "vue";
import ValueDisplayNull from "./ValueDisplayNull.vue";
import ValueDisplayRaw from "./ValueDisplayRaw.vue";
import ValueDisplayBoolean from "./ValueDisplayBoolean.vue";
import ValueDisplayNumber from "./ValueDisplayNumber.vue";
import ValueDisplayString from "./ValueDisplayString.vue";
import ValueDisplayBytes from "./ValueDisplayBytes.vue";
import ValueDisplayDateTime from "./ValueDisplayDateTime.vue";
import ValueDisplayGuid from "./ValueDisplayGuid.vue";
import ValueDisplayNodeId from "./ValueDisplayNodeId.vue";
import ValueDisplayDisplayName from "./ValueDisplayDisplayName.vue";
import ValueDisplayStatusCode from "./ValueDisplayStatusCode.vue";
import ValueDisplayStructure from "./ValueDisplayExtensionObject.vue";
import ValueDisplayArray from "./ValueDisplayArray.vue";

const props = defineProps<{
    variableValue: VariantData | null;
    variableDataType: string | null;
}>();

const displayComponent = computed(() => {
    if (props.variableValue === null) {
        return ValueDisplayNull;
    }

    switch (props.variableValue.type) {
        case "Null":
            return ValueDisplayNull;
        case "Boolean":
            return ValueDisplayBoolean;
        case "SByte":
        case "Byte":
        case "ByteString":
            return ValueDisplayBytes;
        case "Int16":
        case "UInt16":
        case "Int32":
        case "UInt32":
        case "Int64":
        case "UInt64":
        case "Float":
        case "Double":
            return ValueDisplayNumber;
        case "String":
        case "XmlElement":
            return ValueDisplayString;
        case "DateTime":
            return ValueDisplayDateTime;
        case "Guid":
            return ValueDisplayGuid;
        case "NodeId":
        case "ExpandedNodeId":
            return ValueDisplayNodeId;
        case "StatusCode":
            return ValueDisplayStatusCode;
        case "QualifiedName":
        case "LocalizedText":
            return ValueDisplayDisplayName;
        case "ExtensionObject":
            return ValueDisplayStructure;
        case "DataValue":
        case "Variant":
        case "DiagnosticInfo":
        default:
            return ValueDisplayRaw;
    }
});
</script>

<template>
    <ValueDisplayNull v-if="variableValue === null" :value="null" />
    <ValueDisplayArray
        v-else-if="variableValue.isArray"
        :type="variableValue.type"
        :value="variableValue.value"
        :variable-data-type="variableDataType"
    />
    <!-- null scalars (e.g. an empty String) are shown as "null" -->
    <ValueDisplayNull v-else-if="variableValue.value === null" :value="null" />
    <component
        v-else
        :is="displayComponent"
        :value="variableValue.value"
        :data-type="variableDataType"
    />
</template>
