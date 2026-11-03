<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import MiniMethodLine from "./MiniMethodLine.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();
</script>

<template>
    <div>
        <div class="flex flex-col flex-wrap justify-start items-start">
            <MiniMethodLine
                v-for="methodFeature in feature.features"
                :feature="methodFeature"
            ></MiniMethodLine>
        </div>
    </div>
</template>
