<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import MethodFeature from "./MethodFeature.vue";

defineProps<{
    feature: FeatureNode;
}>();
</script>

<template>
    <div>
        <div class="font-semibold">MethodSet</div>

        <div class="flex flex-col flex-wrap justify-start items-start gap-4">
            <MethodFeature
                v-for="feature in feature.features"
                :feature="feature"
            ></MethodFeature>
        </div>
    </div>
</template>
