<script setup lang="ts">
import type { ComponentEntityData } from "@/types/EntityTypes";
import type { ComponentNode, FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import ComponentTitle from "./component/ComponentTitle.vue";
import ComponentFolders from "./component/ComponentFolders.vue";

const props = defineProps<{
    feature: FeatureNode | ComponentNode; // This is fine as this "Feature" is only a stub for the Entity Page
}>();

const entity = computed(() => {
    return props.feature.entity as ComponentEntityData;
});

// First level only: children are listed, but never rendered recursively
const children = computed<ComponentNode[]>(
    () => (props.feature as ComponentNode).children ?? [],
);
</script>

<template>
    <div class="flex flex-col justify-start items-start gap-y-2">
        <ComponentTitle :feature="feature"></ComponentTitle>
        <ComponentFolders :feature="feature"></ComponentFolders>
    </div>
</template>
