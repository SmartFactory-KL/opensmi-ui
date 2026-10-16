<script setup lang="ts">
import type { ComponentNode } from "@/types/NodeFeatureTypes";

import { computed } from "vue";
import { CompassIcon, RobotArmIcon } from "@lucide/vue";

import ClassicLink from "./ClassicLink.vue";
import type { ComponentEntityData } from "@/types/EntityTypes";

const props = defineProps<{
    component: ComponentNode;
}>();

const href = computed(() => {
    return "/component/" + props.component.entityId;
});

const isMachineType = computed(() => {
    return props.component.opcNode.nodeClass == "MachineType";
});

const entity = computed(() => {
    return props.component.entity as ComponentEntityData;
});
</script>

<template>
    <ClassicLink
        :to="href"
        class="flex flex-row justify-start items-center text-blue-800 hover:text-blue-600 gap-x-1"
    >
        <RobotArmIcon v-if="isMachineType" :size="16" />
        <CompassIcon v-else :size="16" />
        <span>{{ entity.name }}</span>
    </ClassicLink>
</template>
