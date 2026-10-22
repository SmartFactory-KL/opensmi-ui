<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import VariableFeature from "./VariableFeature.vue";

defineProps<{
    feature: FeatureNode;
}>();
</script>

<template>
    <div
        class="border border-gray-200 bg-white p-2 shadow-sm flex flex-col gap-y-1"
    >
        <div class="text-stone-800 text-xs">
           {{ feature.entity.name }}
        </div>
        <div>
            <span
                class="text-stone-300 text-xs"
                v-show="feature.features?.length == 0"
                >-empty-</span
            >

            <VariableFeature
                v-for="variableFeature in feature.features"
                :key="variableFeature.entityId"
                class="p-0.5 text-sm"
                :feature="variableFeature"
            >
            </VariableFeature>
        </div>
    </div>
</template>
