<script setup lang="ts">
import type { ComponentNode } from '@/types/NodeFeatureTypes';
import MachineComponentTreeElement from './MachineComponentTreeElement.vue';

defineProps<{
    component: ComponentNode;
}>();
</script>

<template>
    <div>
        <MachineComponentTreeElement :component="component"></MachineComponentTreeElement>
    </div>
</template>
