<script setup lang="ts">
import ServerStateIndicator from "./ServerStateIndicator.vue";
</script>

<template>
    <ServerStateIndicator
        tiny
        @click="$router.push('/connect')"
        class="cursor-pointer active:scale-95"
    ></ServerStateIndicator>
</template>
