<script setup lang="ts">
import type { SkillEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import SkillControlFeature from "./SkillControlFeature.vue";
import MissingFeature from "@/components/MissingFeature.vue";
import VariableContainerFeature from "./VariableContainerFeature.vue";

const props = defineProps<{
    feature: FeatureNode;
    name?: string;
}>();

const entity = computed(() => props.feature.entity as SkillEntityData);

const skillControlFeature = computed(() => {
    for (const feature of props.feature.features) {
        if (feature.entityType === "SkillControl") {
            return feature;
        }
    }
    return null;
});

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
    <section class="border border-slate-200 bg-white text-slate-900 shadow-lg">
        <div class="p-2 text-xs flex flex-row justify-between items-center">
            <div class="font-semibold">
                {{ name?.length ? name : "Generic Skill Name" }}
            </div>
            <div>
                {{ entity.name }}
            </div>
        </div>

        <div>
            <SkillControlFeature
                :feature="skillControlFeature"
                v-if="skillControlFeature !== null"
            ></SkillControlFeature>
            <MissingFeature
                v-else
                expected-feature-type="SkillControl"
            ></MissingFeature>
        </div>

        <div>
            <VariableContainerFeature
                :feature="container"
                :key="container.entityId"
                v-for="container in variableContainers"
            ></VariableContainerFeature>
        </div>
    </section>
</template>
