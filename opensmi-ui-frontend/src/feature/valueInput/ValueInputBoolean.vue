<script setup lang="ts">
import type { VariableModifier } from '@/types/NodeFeatureTypes';

const props = defineProps<{modifiers?: VariableModifier[]}>()
const model = defineModel<boolean | null>({ required: true });
</script>

<template>
    <input type="checkbox" v-model="model" class="size-4 accent-emerald-700" />
</template>
