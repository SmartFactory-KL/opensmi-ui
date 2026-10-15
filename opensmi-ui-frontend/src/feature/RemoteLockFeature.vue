<script setup lang="ts">
import type { FeatureEntityDto, LockingModuleDto } from "@/types/NodeFeatureTypes";
import { computed } from "vue";

const props = defineProps<{
    feature: FeatureEntityDto;
}>();

const remoteLock = computed(() => {
    return props.feature.data as LockingModuleDto;
});
</script>

<template>
    <div>
        {{ remoteLock }}
    </div>
</template>
