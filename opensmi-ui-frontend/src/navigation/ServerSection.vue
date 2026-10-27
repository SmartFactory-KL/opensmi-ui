<script setup lang="ts">
import { RefreshCcwDotIcon, WorkflowIcon } from "@lucide/vue";
import ServerDropdownButton from "./ServerDropdownButton.vue";
import ServerState from "./ServerState.vue";
import { useModelStore } from "@/stores/ModelStore";
import IconButton from "@/components/IconButton.vue";
import QuickConnectButton from "./QuickConnectButton.vue";

const modelStore = useModelStore();
</script>

<template>
    <div class="flex flex-row justify-center items-center gap-x-4">
        <ServerState></ServerState>

        <ServerDropdownButton></ServerDropdownButton>
    </div>
</template>
