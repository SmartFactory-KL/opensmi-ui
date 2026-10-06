<script setup lang="ts">
import { SettingsIcon, ShipWheelIcon } from "@lucide/vue";
import NavigationBrand from "./NavigationBrand.vue";
import NotificationOverview from "./NotificationOverview.vue";
import SocketState from "./SocketState.vue";
import DualClocks from "./DualClocks.vue";
</script>

<template>
    <div
        class="flex flex-row justify-stretch items-center bg-slate-600 h-16 gap-x-2 pr-4"
    >
        <NavigationBrand class="h-16 w-36"></NavigationBrand>

        <div class="grow text-center">MAIN SELECTOR DROPDOWN</div>

        <NotificationOverview></NotificationOverview>

        <DualClocks></DualClocks>

        <SocketState></SocketState>

        <div>
            <SettingsIcon :size="32" class="text-slate-800 fill-slate-400" />
        </div>
    </div>
</template>
