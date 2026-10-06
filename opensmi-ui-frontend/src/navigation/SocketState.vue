<script setup lang="ts">
import { HousePlugIcon, SatelliteIcon } from "@lucide/vue";
import LocalClock from "./LocalClock.vue";
import SocketStateIndicator from "./SocketStateIndicator.vue";
</script>

<template>
    <!-- Main State -->
    <div class="flex flex-row justify-end items-center gap-x-4 mr-2">
        <!-- Socket State Indicator -->
        <SocketStateIndicator></SocketStateIndicator>
    </div>
</template>

<style scoped></style>
