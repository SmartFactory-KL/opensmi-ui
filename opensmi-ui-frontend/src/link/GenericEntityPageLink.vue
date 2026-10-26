<script setup lang="ts">
import { RobotVacuumIcon } from "@lucide/vue";
import { computed } from "vue";

const props = defineProps<{
    entityId: string | string[] | undefined;
    tiny?: boolean;
}>();

const href = computed(() => {
    return "/entity/" + props.entityId;
});
</script>

<template>
    <div v-if="entityId == null || entityId == undefined">
        Invalid Entity Id: {{ entityId }}
    </div>
    <RouterLink
        v-else
        :to="href"
        class="flex flex-row justify-start items-center gap-x-1 border border-pink-300 bg-stone-200 rounded-lg px-1 py-1 shadow-md"
    >
        <RobotVacuumIcon :size="12" class="text-stone-600"></RobotVacuumIcon>
    </RouterLink>
</template>
