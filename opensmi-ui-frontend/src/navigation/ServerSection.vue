<script setup lang="ts">
import { ArrowDownUpIcon, RefreshCcwDotIcon } from "@lucide/vue";
import ServerDropdown from "./ServerDropdown.vue";
import ServerState from "./ServerState.vue";
import { useModelStore } from "@/stores/ModelStore";
import IconButton from "@/components/IconButton.vue";

const modelStore = useModelStore();
</script>

<template>
    <div class="flex flex-row justify-center items-center gap-x-4">
        <ServerDropdown></ServerDropdown>

        <div
            class="bg-slate-100 border-2 border-slate-400 h-14 flex flex-row justify-center items-center gap-x-3 px-2 py-2"
        >
            <IconButton
                @click="modelStore.refreshMachineData()"
                :class="{ 'animate-spin': modelStore.isWorking }"
            >
                <RefreshCcwDotIcon></RefreshCcwDotIcon>
            </IconButton>

            <ServerState></ServerState>
        </div>
    </div>
</template>
