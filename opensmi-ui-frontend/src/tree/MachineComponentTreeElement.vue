<script setup lang="ts">
import ComponentCard from "@/card/ComponentCard.vue";
import ComponentLink from "@/link/ComponentLink.vue";
import type { ComponentDto, ComponentEntityDto } from "@/types/ModuleTypes";
import { computed } from "vue";

const props = defineProps<{
    component: ComponentEntityDto;
}>();

const hasChildElements = computed(() => {
    return props.component?.children?.length;
});
</script>

<template>
    <div>
        <div class="flex flex-row justify-start items-center">
            <ComponentLink :component="component"></ComponentLink>
            <!-- <ComponentCard :component="component"></ComponentCard> -->
        </div>
        <div>
            <div
                v-for="feature in component.features"
                class="text-xs font-thin ml-2"
            >
                + {{ feature.entityType }} [{{ feature.data?.name || "" }}]
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
