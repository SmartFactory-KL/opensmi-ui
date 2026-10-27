<script setup lang="ts">
import type { VariableEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import FeatureErrorWrapper from "./FeatureErrorWrapper.vue";
import ValueDisplay from "./variables/ValueDisplay.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => {
    return props.feature.entity as VariableEntityData;
});
</script>

<template>
    <FeatureErrorWrapper :feature="feature" v-slot="{ feature }">
        <div
            class="flex flex-col justify-start items-start bg-white border border-stone-200 text-emerald-900 p-1"
        >
            <div>
                <ValueDisplay :variableValue="entity.value"></ValueDisplay>
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
    </FeatureErrorWrapper>
</template>
