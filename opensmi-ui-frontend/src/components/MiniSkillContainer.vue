<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import MiniSkillLine from "./MiniSkillLine.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();
</script>

<template>
    <div>
        <div class="flex flex-col flex-wrap justify-start items-start">
            <div v-for="groupFeature in feature.features">
                <MiniSkillLine
                    v-for="skillFeature in groupFeature.features"
                    :name="groupFeature.entity.name"
                    :is-continuous="groupFeature.entity.isContinuous"
                    :is-group="groupFeature?.features?.length > 1"
                    :feature="skillFeature"
                ></MiniSkillLine>
            </div>
        </div>
    </div>
</template>
