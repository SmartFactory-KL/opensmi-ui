<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import SkillFeature from "./SkillFeature.vue";
import SkillMiniFeature from "./SkillMiniFeature.vue";
import { computed } from "vue";

const props = defineProps<{
    feature: FeatureNode;
    tiny?: boolean;
}>();

const skillFeatureToUse = computed(() => {
    if (props.tiny === true) {
        return SkillMiniFeature;
    }

    return SkillFeature;
});
</script>

<template>
    <!-- If only a single skill is present, directly show that -->
    <div v-if="feature.features && feature.features.length === 1">
        <component
            :is="skillFeatureToUse"
            :feature="feature.features[0]!"
            :name="feature.entity.name"
        ></component>
    </div>

    <!-- Only show Group Information for skills with anything else other then only the Execution -->
    <div v-else class="bg-white p-1 flex flex-col justify-start items-start">
        <div><span class="font-semibold">{{ feature.entity.name }}</span> SkillGroup</div>
        <component
            :is="skillFeatureToUse"
            v-for="feature in feature.features"
            :feature="feature"
            :name="feature.entity.name"
        ></component>
    </div>
</template>
