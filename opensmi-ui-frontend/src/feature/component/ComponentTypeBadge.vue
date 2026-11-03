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
    <div
        class="bg-emerald-200 rounded-lg font-light py-1 px-2 text-xs text-slate-600"
    >
        {{ entity.componentType }}
    </div>
</template>
