<script setup lang="ts">
import type { VariableEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed, toRaw } from "vue";
import ValueDisplay from "./valueDisplay/ValueDisplay.vue";
import { onMounted } from "vue";
import { ref } from "vue";
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

const unitModifier = computed(() => {
    if (!entity.value?.modifiers?.length) {
        return null;
    }

    for (const mod of entity.value.modifiers) {
        if (mod.modifierType == "UnitModifier") {
            return mod.modifierContent;
        }
    }

    return null;
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
        class="flex flex-col justify-start items-stretch  text-emerald-900 border-l-4 border-l-slate-600"
    >
        <div class="flex flex-row gap-x-2 px-2 pt-1 min-h-8 bg-stone-100">
            <div
                v-if="entity.isWritable"
                class="grow grid grid-cols-[1fr_auto_1fr] items-center gap-x-1"
            >
                <ValueInput
                    v-model="tempValue"
                    :modifiers="entity.modifiers"
                    class="min-w-0 w-full"
                ></ValueInput>

                <ArrowRightIcon
                    @click="setValue"
                    :size="16"
                    class="cursor-pointer active:scale-90 size-4"
                ></ArrowRightIcon>

                <ValueDisplay
                    :variableValue="entity.value"
                    :modifiers="entity.modifiers"
                    class="min-w-0"
                ></ValueDisplay>
            </div>

            <div v-else class="growbg-stone-200">
                <ValueDisplay
                    :variableValue="entity.value"
                    :modifiers="entity.modifiers"
                    class="grow"
                ></ValueDisplay>
            </div>
        </div>
        <div
            class="text-xs bg-red-50 text-red-500 p-1"
            v-if="feature.initState !== 'done'"
        >
            Error: {{ feature.initError }}
        </div>
        <div
            class="w-full flex flex-row justify-between items-center text-xs text-stone-400 bg-white gap-x-2 px-2 py-0.5"
        >
            <div class="flex flex-row justify-start gap-x-1 items-center">
                {{ entity.name }}
                <div v-if="unitModifier">
                    [{{ unitModifier.displayName.text }}]
                </div>
            </div>

            <span class="font-light">
                {{ entity.dataType }} |
                <span v-if="entity.lastUpdatedAt">{{
                    new Date(entity.lastUpdatedAt).toLocaleString()
                }}</span>
            </span>
        </div>
    </div>
</template>
