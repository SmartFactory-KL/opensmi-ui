<script setup lang="ts">
import ServerDropdown from "./ServerDropdown.vue";
import ServerState from "./ServerState.vue";
</script>

<template>
    <div class="flex flex-row justify-center items-center gap-x-4">
        <ServerDropdown></ServerDropdown>

        <ServerState></ServerState>
    </div>
</template>
