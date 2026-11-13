<script setup lang="ts">
import ModelStateIndicator from "./ModelStateIndicator.vue";
import ServerDropdownButton from "./ServerDropdownButton.vue";
import ServerState from "./ServerState.vue";
import { useModelStore } from "@/stores/ModelStore";

const modelStore = useModelStore();
</script>

<template>
    <div class="flex flex-row justify-center items-center gap-x-4">
        <ServerState></ServerState>
        <ModelStateIndicator :state="modelStore.state"></ModelStateIndicator>
        <ServerDropdownButton></ServerDropdownButton>
    </div>
</template>
