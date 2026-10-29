<script setup lang="ts">
import ExpectedFeature from "@/components/ExpectedFeature.vue";
import LockFeature from "@/feature/basic/LockFeature.vue";
import MachineryItemStateFeature from "@/feature/basic/MachineryItemStateFeature.vue";
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

            <ExpectedFeature
                :expected-feature="stateFeature"
                expectedFeatureType="MachineryItemState"
                optional
                v-slot="{ feature }"
            >
                <MachineryItemStateFeature
                    :feature="feature"
                    class="text-xs"
                ></MachineryItemStateFeature>
            </ExpectedFeature>
        </div>

        <div class="flex flex-col justify-start items-center gap-2">
            <ExpectedFeature
                :expected-feature="lockFeature"
                expectedFeatureType="Lock"
                optional
                v-slot="{ feature }"
            >
                <LockFeature
                    :feature="feature"
                    @click.stop
                    :dark="!active"
                ></LockFeature>
            </ExpectedFeature>
        </div>
    </div>
</template>
