<script setup lang="ts">
import type { MachineryItemStateEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => {
    return props.feature.entity as MachineryItemStateEntityData;
});
</script>

<template>
    <span>{{ entity.currentState?.text || "unknown" }}</span>
</template>
