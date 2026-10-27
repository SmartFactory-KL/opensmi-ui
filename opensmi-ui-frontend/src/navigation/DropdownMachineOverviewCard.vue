<script setup lang="ts">
import LockFeature from "@/feature/LockFeature.vue";
import MachineryItemStateFeature from "@/feature/MachineryItemStateFeature.vue";
import type { ComponentNode, FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";

const props = defineProps<{
    component: ComponentNode;
    active?: boolean;
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
        class="flex flex-col justify-between items-stretch p-3 gap-x-1"
        :class="
            active
                ? 'bg-slate-300 text-slate-800'
                : 'bg-slate-600 text-slate-50'
        "
    >
        <div class="flex flex-col justify-between items-center mb-2 gap-x-2">
            <div class="font-semibold">
                {{ component.entity.name }}
            </div>

            <MachineryItemStateFeature
                v-if="stateFeature !== null"
                :feature="stateFeature"
                class="text-xs"
            ></MachineryItemStateFeature>
        </div>

        <div class="flex flex-col justify-start items-center gap-2">
            <LockFeature
                v-if="lockFeature !== null"
                :feature="lockFeature"
                @click.stop
                :dark="!active"
            ></LockFeature>
        </div>
    </div>
</template>
