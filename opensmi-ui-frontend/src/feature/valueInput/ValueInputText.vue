<script setup lang="ts">
import type { VariantData } from '@/types/OPCTypes';

const props = defineProps<{
    value: VariantData | null;
}>();
</script>

<template>
    <div v-if="value">
        <input type="text" v-model="value.value" class="min-w-10 min-h-4"></input>
    </div>
</template>
