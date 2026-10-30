<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import VariableFeature from "./VariableFeature.vue";

defineProps<{
    feature: FeatureNode;
}>();
</script>

<template>
    <div class="flex flex-col w-full">
        <div class="border-l-4 border-l-slate-600 bg-indigo-100 px-4">
            {{ feature.entity.name }}
        </div>
        <div class="flex flex-col justify-start items-stretch">
            <span class="text-xs" v-show="feature.features?.length == 0"
                >-empty-</span
            >

            <VariableFeature
                v-for="variableFeature in feature.features"
                :key="variableFeature.entityId"
                :feature="variableFeature"
            >
            </VariableFeature>
        </div>
    </div>
</template>
