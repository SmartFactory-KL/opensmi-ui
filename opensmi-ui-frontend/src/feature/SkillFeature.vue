<script setup lang="ts">
import type { SkillEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import GenericFeature from "./GenericFeature.vue";
import { simplyPostToText } from "@/fetch/simplyFetch";
import type { SkillControlAction } from "@/types/UpdateTypes";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => props.feature.entity as SkillEntityData);
</script>

<template>
    <section class="w-full border border-slate-200 bg-white text-slate-900">
        {{ entity }}

        <GenericFeature
            :feature="childFeature"
            v-for="childFeature in feature.features"
        ></GenericFeature>
    </section>
</template>
