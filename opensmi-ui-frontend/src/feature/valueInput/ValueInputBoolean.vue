<script setup lang="ts">
const model = defineModel<boolean | null>({ required: true });
</script>

<template>
    <input type="checkbox" v-model="model" class="size-4 accent-emerald-700" />
</template>
