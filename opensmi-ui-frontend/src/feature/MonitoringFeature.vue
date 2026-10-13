<script setup lang="ts">
import type { FeatureEntityDto } from "@/types/ModuleTypes";
import VariableTreeFeature from "./VariableTreeFeature.vue";

const props = defineProps<{
    feature: FeatureEntityDto;
}>();
</script>

<template>
    <VariableTreeFeature :items="feature.data" label="Monitoring"></VariableTreeFeature>
</template>
