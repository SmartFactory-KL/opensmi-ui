<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import SkillFeature from "./SkillFeature.vue";
import { computed } from "vue";

const props = defineProps<{
    feature: FeatureNode;
}>();
</script>

<template>
    <!-- If only a single skill is present, directly show that -->
    <div v-if="feature.features && feature.features.length === 1">
        <SkillFeature
            :feature="feature.features[0]!"
            :name="feature.entity.name"
        ></SkillFeature>
    </div>

    <!-- Only show Group Information for skills with anything else other then only the Execution -->
    <div
        v-else
        class="py-2 pr-2 pl-4 border-l-4 border-l-indigo-100 bg-indigo-50 flex flex-col justify-start items-start"
    >
        <div>
            <span class="font-semibold">{{ feature.entity.name }}</span>
            SkillGroup
        </div>
        <SkillFeature
            v-for="feature in feature.features"
            :feature="feature"
            :name="feature.entity.name"
        ></SkillFeature>
    </div>
</template>
