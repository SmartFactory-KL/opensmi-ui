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
        <ServerDropdownButton></ServerDropdownButton>

        <div
            class="bg-slate-100 border-2 border-slate-400 h-14 flex flex-row justify-center items-center gap-x-3 px-2 py-2"
        >
            <IconButton
                @click="modelStore.loadModel()"
                :disabled="modelStore.isWorking"
            >
                <RefreshCcwDotIcon
                    :class="{ 'animate-spin': modelStore.isWorking }"
                ></RefreshCcwDotIcon>
            </IconButton>

            <IconButton
                @click="modelStore.requestBrowsing()"
                :disabled="modelStore.isWorking"
            >
                <WorkflowIcon
                    :class="{ 'animate-spin': modelStore.isWorking }"
                ></WorkflowIcon>
            </IconButton>

            <ServerState></ServerState>

            <QuickConnectButton></QuickConnectButton>
        </div>
    </div>
</template>
