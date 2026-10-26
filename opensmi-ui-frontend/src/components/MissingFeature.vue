<script setup lang="ts">
defineProps<{
    expectedFeatureType: string;
}>();
</script>

<template>
    <div class="text-red-800 bg-red-200 border border-red-600 px-4 text-sm">
        This feature is missing an expected sub feature of type
        {{ expectedFeatureType }}!
    </div>
</template>
