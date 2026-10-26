<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import SkillFeature from "./SkillFeature.vue";

defineProps<{
    feature: FeatureNode;
}>();
</script>

<template>
    <!-- If only a single skill is present, directly show that -->
    <div v-if="feature.features && feature.features.length === 1">
        <SkillFeature :feature="feature.features[0]!" :name="feature.entity.name"></SkillFeature>
    </div>

    <!-- Only show Group Information for skills with anything else other then only the Execution -->
    <div v-else>
        <div>SkillGroup for {{ feature.opcNode.browseName }}</div>
        <SkillFeature
            v-for="feature in feature.features"
            :feature="feature"
        ></SkillFeature>
    </div>
</template>
