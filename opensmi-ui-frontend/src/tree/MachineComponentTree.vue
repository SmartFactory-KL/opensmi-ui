<script setup lang="ts">
import type { ComponentEntityDto, MachineDto } from '@/types/NodeFeatureTypes';
import MachineComponentTreeElement from './MachineComponentTreeElement.vue';

defineProps<{
    component: ComponentEntityDto;
}>();
</script>

<template>
    <div>
        <MachineComponentTreeElement :component="component"></MachineComponentTreeElement>
    </div>
</template>
