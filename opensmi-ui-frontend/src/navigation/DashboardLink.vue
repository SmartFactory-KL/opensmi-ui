<script setup lang="ts">
import { LayoutDashboardIcon } from "@lucide/vue";
</script>

<template>
    <button
        type="button"
        title="Dashboard: Open the dashboard overview."
        aria-label="Dashboard"
        :class="[
            'flex size-11 cursor-pointer items-center justify-center rounded-md border shadow-sm',
            'bg-stone-200 border-stone-200 text-stone-600',
            'transition-colors duration-100 hover:bg-stone-300 active:scale-95',
        ]"
        @click="$router.push('/dashboard')"
    >
        <LayoutDashboardIcon class="size-6 text-stone-500" :stroke-width="2" />
    </button>
</template>
