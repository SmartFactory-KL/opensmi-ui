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
    <div class="p-2 bg-white border">{{ entity.currentState }}</div>
</template>
