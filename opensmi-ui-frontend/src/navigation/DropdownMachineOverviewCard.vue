<script setup lang="ts">
import LockFeature from "@/feature/LockFeature.vue";
import MachineryItemStateFeature from "@/feature/MachineryItemStateFeature.vue";
import type { ComponentNode, FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";

const props = defineProps<{
    component: ComponentNode;
}>();

const stateFeature = computed<FeatureNode | null>(() => {
    for (const feature of props.component.features) {
        if (feature.entityType == "MachineryItemState") {
            return feature;
        }
    }

    return null;
});

const lockFeature = computed(() => {
    for (const feature of props.component.features) {
        if (feature.entityType == "Lock") {
            return feature;
        }
    }

    return null;
});
</script>

<template>
    <div
        class="flex flex-col justify-between items-stretch p-3 gap-x-1 bg-white shadow-md border border-slate-500"
    >
        <div class="flex flex-row justify-between items-center mb-2 gap-x-2">
            <div class="font-semibold">
                {{ component.entity.name }}
            </div>

            <MachineryItemStateFeature
                v-if="stateFeature !== null"
                :feature="stateFeature"
                class="text-xs"
            ></MachineryItemStateFeature>
        </div>

        <div class="flex flex-col justify-start items-start gap-2">
            <LockFeature
                v-if="lockFeature !== null"
                :feature="lockFeature"
            ></LockFeature>
        </div>
    </div>
</template>
