<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";

const props = defineProps<{
    feature: FeatureNode;
}>();
</script>

<template>
    <div>
        <div class="flex flex-col flex-wrap justify-start items-start">
            <div v-for="feature in feature.features"></div>
        </div>
    </div>
</template>
