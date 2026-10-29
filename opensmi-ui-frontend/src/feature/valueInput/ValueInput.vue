<script setup lang="ts">
import type { VariantData } from "@/types/OPCTypes";
import ValueInputArray from "./ValueInputArray.vue";
import ValueInputScalar from "./ValueInputScalar.vue";

// Usage: <ValueInput v-model="tempValue" />
const variant = defineModel<VariantData | null>({ required: true });

function setScalar(value: unknown) {
    if (variant.value === null) return;
    variant.value = { ...variant.value, value } as VariantData;
}
</script>

<template>
    <!-- without a VariantData there is no type to edit against -->
    <span v-if="variant === null" class="text-sm text-stone-400">null</span>
    <ValueInputArray v-else-if="variant.isArray" v-model="variant" />
    <ValueInputScalar
        v-else
        :type="variant.type"
        :model-value="variant.value"
        @update:model-value="setScalar"
    />
</template>
