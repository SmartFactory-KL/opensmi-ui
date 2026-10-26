<script setup lang="ts">
import ComponentLink from "@/link/ComponentLink.vue";
import type { ComponentNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";

const props = defineProps<{
    component: ComponentNode;
}>();

const hasChildElements = computed(() => {
    return props.component?.children?.length;
});
</script>

<template>
    <div>
        <div class="flex flex-row justify-start items-center">
            <ComponentLink :component="component"></ComponentLink>
        </div>
        <div>
            <div
                v-for="feature in component.features"
                class="text-xs font-thin ml-2"
            >
                <span class="font-normal">
                    + {{ feature.entity.name || "" }}
                </span> [{{ feature.entityType }}]
            </div>
        </div>
        <div v-if="hasChildElements" class="ml-4">
            <MachineComponentTreeElement
                :component="childComponent"
                v-for="childComponent in component.children"
            ></MachineComponentTreeElement>
        </div>
    </div>
</template>
