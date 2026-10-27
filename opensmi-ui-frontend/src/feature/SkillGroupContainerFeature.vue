<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import SkillGroupFeature from "./SkillGroupFeature.vue";

defineProps<{
    feature: FeatureNode;
}>();
</script>

<template>
    <div>
        <div class="font-semibold">SkillSet</div>

        <div class="flex flex-row flex-wrap justify-start items-start gap-4">
            <SkillGroupFeature
                v-for="feature in feature.features"
                :feature="feature"
            ></SkillGroupFeature>
        </div>
    </div>
</template>
