<script setup lang="ts">
import { computed, type Component } from "vue";
import ValueInputBoolean from "./ValueInputBoolean.vue";
import ValueInputDateTime from "./ValueInputDatetime.vue";
import ValueInputExpandedNodeId from "./ValueInputExpandedNodeId.vue";
import ValueInputFloat from "./ValueInputFloat.vue";
import ValueInputInteger from "./ValueInputInteger.vue";
import ValueInputJson from "./ValueInputJSON.vue";
import ValueInputLocalizedText from "./ValueInputLocalizedText.vue";
import ValueInputNodeId from "./ValueInputNodeId.vue";
import ValueInputQualifiedName from "./ValueInputQualifiedName.vue";
import ValueInputStatusCode from "./ValueInputStatusCode.vue";
import ValueInputText from "./ValueInputText.vue";

const props = defineProps<{ type: string }>();
const model = defineModel<any>({ required: true });

interface Resolved {
    component: Component;
    props: Record<string, unknown>;
}

const resolved = computed<Resolved | null>(() => {
    switch (props.type) {
        case "Null":
            return null;
        case "Boolean":
            return { component: ValueInputBoolean, props: {} };
        case "SByte":
        case "Byte":
        case "Int16":
        case "UInt16":
        case "Int32":
        case "UInt32":
        case "Int64":
        case "UInt64":
            return { component: ValueInputInteger, props: { type: props.type } };
        case "Float":
        case "Double":
            return { component: ValueInputFloat, props: {} };
        case "String":
        case "XmlElement":
            return { component: ValueInputText, props: { kind: "string" } };
        case "Guid":
            return { component: ValueInputText, props: { kind: "guid" } };
        case "ByteString":
            return { component: ValueInputText, props: { kind: "base64" } };
        case "DateTime":
            return { component: ValueInputDateTime, props: {} };
        case "NodeId":
            return { component: ValueInputNodeId, props: {} };
        case "ExpandedNodeId":
            return { component: ValueInputExpandedNodeId, props: {} };
        case "QualifiedName":
            return { component: ValueInputQualifiedName, props: {} };
        case "LocalizedText":
            return { component: ValueInputLocalizedText, props: {} };
        case "StatusCode":
            return { component: ValueInputStatusCode, props: {} };
        // ExtensionObject, DataValue, Variant, DiagnosticInfo and anything unknown
        default:
            return { component: ValueInputJson, props: {} };
    }
});
</script>

<template>
    <span v-if="resolved === null" class="text-sm text-stone-400">null</span>
    <component :is="resolved.component" v-else v-bind="resolved.props" v-model="model" />
</template>
