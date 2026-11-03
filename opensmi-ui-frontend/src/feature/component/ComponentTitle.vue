<script setup lang="ts">
import type { ComponentEntityData } from "@/types/EntityTypes";
import type { ComponentNode, FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";

const props = defineProps<{
    feature: FeatureNode | ComponentNode; // This is fine as this "Feature" is only a stub for the Entity Page
}>();

const entity = computed(() => {
    return props.feature.entity as ComponentEntityData;
});
</script>

<template>
    <div class="flex flex-col jusitfy-start items-start gap-2">
        <div class="font-semibold text-xl">{{ entity.name }}</div>
    </div>
</template>
