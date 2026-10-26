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
    <div>
        <div class="font-semibold">Component</div>

        <div class="flex flex-col flex-wrap justify-start items-start gap-4">
            {{ entity.name }}
        </div>
    </div>
</template>
