<script setup lang="ts">
import { HousePlugIcon, SatelliteIcon } from "@lucide/vue";
import LocalClock from "./LocalClock.vue";
import { useServerStore } from "@/stores/ServerSessionStore";

const serverStore = useServerStore();
</script>

<template>
    <!-- Clocks -->
    <div
        class="flex flex-col justify-center items-center border-2 border-slate-500 px-2 py-1 rounded-md bg-slate-200"
    >
        <div
            class="server-clock font-mono text-sm flex flex-row justify-center items-center gap-x-1"
            :class="
                serverStore.isConnected
                    ? ['text-green-400']
                    : ['text-slate-400']
            "
        >
            <SatelliteIcon :size="16"></SatelliteIcon>
            {{ serverStore.serverTime }}
        </div>
        <div
            class="local-clock font-mono text-sm text-blue-400 flex flex-row justify-center items-center gap-x-1"
        >
            <HousePlugIcon :size="16"></HousePlugIcon>
            <LocalClock></LocalClock>
        </div>
    </div>
</template>
