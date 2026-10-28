<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import SkillGroupFeature from "./SkillGroupFeature.vue";

const props = defineProps<{
    feature: FeatureNode;
    tiny?: boolean;
    asColumn?: boolean;
}>();
</script>

<template>
    <div>
        <div
            class="flex flex-wrap justify-start items-start"
            :class="[asColumn ? 'flex-col' : 'flex-row']"
        >
            <SkillGroupFeature
                v-for="feature in feature.features"
                :feature="feature"
                :tiny="tiny"
            ></SkillGroupFeature>
        </div>
    </div>
</template>
