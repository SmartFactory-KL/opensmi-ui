<script setup lang="ts">
import type { SkillEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import VariableContainerFeature from "./VariableContainerFeature.vue";
import ValueDisplayNodeId from "./valueDisplay/ValueDisplayNodeId.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => props.feature.entity as SkillEntityData);

const variableContainers = computed(() => {
    const result: FeatureNode[] = [];
    for (const feature of props.feature.features) {
        if (feature.entityType === "VariableContainer") {
            result.push(feature);
        }
    }

    return result;
});
</script>

<template>
    <section class="bg-white text-slate-900 shadow-lg">
        <div
            class="p-2 flex flex-col justify-start items-start bg-lime-600 text-slate-200 cursor-pointer"
        >
            {{ entity.name }}
            <ValueDisplayNodeId
                :value="feature.opcNode.nodeId"
            ></ValueDisplayNodeId>
        </div>

        <div>
            <VariableContainerFeature
                v-for="container in variableContainers"
                :feature="container"
            ></VariableContainerFeature>
        </div>
    </section>
</template>
