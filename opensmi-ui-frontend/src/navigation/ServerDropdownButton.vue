<script setup lang="ts">
import { useDropdownStore } from "@/stores/DropdownStore";
import { useModelStore } from "@/stores/ModelStore";
import { ArrowBigDownIcon } from "@lucide/vue";

const modelStore = useModelStore();
const dropdownStore = useDropdownStore();

function toggleModelDropdown() {
    dropdownStore.toggleDropdown();
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
            <ArrowBigDownIcon
                :class="{ 'rotate-180': dropdownStore.isVisible }"
                class="transition-transform duration-200 ease-out"
            ></ArrowBigDownIcon>
        </div>
    </div>
</template>
