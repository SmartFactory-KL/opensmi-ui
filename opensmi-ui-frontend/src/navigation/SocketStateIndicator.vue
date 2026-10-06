<script setup lang="ts">
import { ArrowDownIcon, MonitorCheckIcon, MonitorOffIcon } from "@lucide/vue";
</script>

<template>
    <div
        class="flex flex-col items-center border-4 rounded-lg h-14 w-14 p-0.5 border-green-600 bg-green-100 shadow-lg"
    >
        <MonitorCheckIcon :size="32" class="text-green-500" />
        <!-- <MonitorOffIcon :size="32" class="w-10 text-green-500" /> -->

        <div class="flex flex-row justify-center items-center">
            <ArrowDownIcon :size="10"></ArrowDownIcon>
            <span class="text-xs">283</span>
        </div>
    </div>
</template>
