<script setup lang="ts">
import { HousePlugIcon, SatelliteIcon } from "@lucide/vue";
import LocalClock from "./LocalClock.vue";
</script>

<template>
    <!-- Clocks -->
    <div
        class="flex flex-col justify-center items-center border-2 border-slate-500 px-2 py-1 rounded-md bg-slate-200"
    >
        <div
            class="server-clock font-mono text-sm text-slate-400 flex flex-row justify-center items-center gap-x-1"
        >
            <SatelliteIcon :size="16"></SatelliteIcon>
            --:--:--
        </div>
        <div
            class="local-clock font-mono text-sm text-blue-400 flex flex-row justify-center items-center gap-x-1"
        >
            <HousePlugIcon :size="16"></HousePlugIcon>
            <LocalClock></LocalClock>
        </div>
    </div>
</template>
