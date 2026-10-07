<script setup lang="ts">
import { AlertCircleIcon } from "@lucide/vue";

defineProps<{
    error: string | null;
}>();
</script>

<template>
    <div
        v-if="error !== null"
        class="mx-6 mt-6 flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-800"
    >
        <AlertCircleIcon class="mt-0.5 h-5 w-5 shrink-0" />
        <div class="min-w-0">
            <p class="font-medium">Something went wrong</p>
            <p class="mt-0.5 text-sm text-red-700">
                {{ error }}
            </p>
        </div>
    </div>
</template>
