<script setup lang="ts">
import NavigationBrand from "./NavigationBrand.vue";
import NotificationOverview from "./NotificationOverview.vue";
import SocketState from "./SocketState.vue";
import DualClocks from "./DualClocks.vue";
import ServerSection from "./ServerSection.vue";
</script>

<template>
    <div
        class="flex flex-row flex-wrap justify-stretch items-center bg-slate-800 h-16 gap-x-2"
    >
        <NavigationBrand class="h-16 w-36"></NavigationBrand>

        <ServerSection class="grow"></ServerSection>

        <NotificationOverview></NotificationOverview>

        <DualClocks></DualClocks>

        <SocketState></SocketState>
    </div>
</template>
