<script setup lang="ts">
import type { ComponentDto, ComponentEntityDto } from "@/types/ModuleTypes";

import { computed } from "vue";
import { CompassIcon, RobotArmIcon } from "@lucide/vue";

import ClassicLink from "./ClassicLink.vue";

const props = defineProps<{
    component: ComponentEntityDto;
}>();

const href = computed(() => {
    return "/component/" + props.component.entityId;
});

const isMachineType = computed(() => {
  return props.component.data.uaType == "MachineType"
})
</script>

<template>
    <ClassicLink
        :to="href"
        class="flex flex-row justify-start items-center text-blue-800 hover:text-blue-600 gap-x-1"
    >
        <RobotArmIcon v-if="isMachineType" :size="16" />
        <CompassIcon v-else :size="16" />
        <span>{{ component.data.name }}</span>
    </ClassicLink>
</template>
