<script setup lang="ts">
import type { VariableEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed, toRaw } from "vue";
import ValueDisplay from "./valueDisplay/ValueDisplay.vue";
import { onMounted } from "vue";
import { ref } from "vue";
import IconButton from "@/components/IconButton.vue";
import { ArrowRightIcon } from "@lucide/vue";
import Toaster from "@/toast/Toaster";
import { simplyPostToText } from "@/fetch/simplyFetch";
import ValueInput from "./valueInput/ValueInput.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => {
    return props.feature.entity as VariableEntityData;
});

const tempValue = ref<any>(null);

onMounted(() => {
    const val = toRaw(entity.value.value);
    tempValue.value = structuredClone(val);
});

async function setValue() {
    try {
        const valueToWrite = tempValue.value;

        const action = {
            entityId: props.feature.entityId,
            actionType: "VariableValueWriteAction",
            action: {
                newValue: valueToWrite,
            },
        };

        await simplyPostToText("/api/opc-model/action", action);
    } catch (e) {
        console.error(e);
        Toaster.error("Failed to call skill action: " + e);
    }
}
</script>

<template>
    <div
        class="flex flex-col justify-start items-start bg-white border border-stone-200 text-emerald-900 p-1"
    >
        <div class="flex flex-row justify-around gap-x-2 items-center">
            <ValueInput :variableValue="tempValue" class="grow"></ValueInput>

            <ArrowRightIcon
                @click="setValue"
                :size="16"
                class="cursor-pointer active:scale-90"
            ></ArrowRightIcon>

            <ValueDisplay
                :variableValue="entity.value"
                class="grow"
            ></ValueDisplay>
        </div>
        <div
            class="w-full flex flex-row justify-between items-center text-xs text-stone-600 gap-x-2"
        >
            <span>
                {{ entity.name }}
            </span>

            <span>
                {{ entity.dataType }}
            </span>

            <span v-if="entity.lastUpdatedAt">
                {{ new Date(entity.lastUpdatedAt).toLocaleString() }}
            </span>
        </div>
    </div>
</template>
