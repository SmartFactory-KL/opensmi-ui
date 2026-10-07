<script setup lang="ts">
import { useModelStore } from "@/stores/ModelStore";
import { ArrowBigDown, ArrowBigDownIcon } from "@lucide/vue";

const modelStore = useModelStore();

function toggleModelDropdown() {
    console.log("TOGGLE");
}
</script>

<template>
    <div
        class="flex flex-row justify-between items-center gap-x-4 px-4 py-2 bg-slate-100 rounded-md active:scale-[0.99] cursor-pointer min-w-1/2"
        @click="toggleModelDropdown"
    >
        <div class="text-lg">
            Server with {{ modelStore.machines?.size || 0 }} Machines
        </div>
        <div class="border-l border-l-slate-500 pl-2">
            <ArrowBigDownIcon></ArrowBigDownIcon>
        </div>
    </div>
</template>
