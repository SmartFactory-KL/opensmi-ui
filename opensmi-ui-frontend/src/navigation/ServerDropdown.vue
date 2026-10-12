<script setup lang="ts">
import { useDropdownStore } from "@/stores/DropdownStore";
import { useModelStore } from "@/stores/ModelStore";
import MachineComponentTree from "@/tree/MachineComponentTree.vue";
import ServerStateIndicator from "./ServerStateIndicator.vue";
import ComponentCard from "@/card/ComponentCard.vue";

const dropdownStore = useDropdownStore();
const modelStore = useModelStore();
</script>

<template>
    <Transition
        enter-active-class="transition-all duration-150 ease-out"
        enter-from-class="max-h-0 -translate-y-2 opacity-0"
        enter-to-class="max-h-[80vh] translate-y-0 opacity-100"
        leave-active-class="transition-all duration-100 ease-in"
        leave-from-class="max-h-[80vh] translate-y-0 opacity-100"
        leave-to-class="max-h-0 -translate-y-2 opacity-0"
    >
        <div
            v-if="dropdownStore.isVisible"
            class="flex items-start px-24 pt-3 bg-stone-200/50 z-10"
            @click.self.prevent="dropdownStore.closeDropdown()"
        >
            <div
                class="z-20 w-full overflow-hidden rounded-xl border border-slate-200 bg-slate-300 shadow-2xl shadow-slate-900/10 backdrop-blur-sm"
            >
                <div class="my-3 max-h-[calc(80vh-2rem)] overflow-y-auto px-4">
                    <div class="dropdown-grid">
                        <div
                            class="dropdown-tree overflow-auto max-h-[calc(80vh-2rem)] bg-slate-200 border-4 border-slate-400 p-4"
                        >
                            <span
                                v-show="modelStore.isWorking"
                                class="text-center text-pink-500 text-xs"
                            >
                                Laden...
                            </span>
                            <div
                                v-for="rootComponent in modelStore.rootComponents.values()"
                                class="mb-10 border-b border-b-pink-500"
                            >
                                <MachineComponentTree
                                    :component="rootComponent"
                                ></MachineComponentTree>
                            </div>
                        </div>
                        <div
                            class="dropdown-state flex flex-row justify-center items-center"
                        >
                            <!-- Current state -->
                            <ServerStateIndicator @click="dropdownStore.closeDropdown()"></ServerStateIndicator>
                        </div>
                        <div
                            class="dropdown-overview px-4 py-0 flex flex-col gap-3"
                        >
                            <span
                                v-show="modelStore.isWorking"
                                class="text-center text-pink-500 text-xs"
                            >
                                Laden...
                            </span>
                            <span
                                v-show="
                                    !modelStore.isWorking &&
                                    modelStore.rootComponents?.size == 0
                                "
                                class="text-center text-stone-400 text-xs"
                            >
                                Nothing to show
                            </span>
                            <ComponentCard
                                v-for="machine in modelStore.rootComponents.values()"
                                :component="machine"
                            >
                            </ComponentCard>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </Transition>
</template>

<style scoped>
.dropdown-grid {
    display: grid;
    grid-template-rows: 6rem 1fr;
    grid-template-columns: 1fr 50%;
    grid-template-areas:
        "tree state"
        "tree overview";
}

.dropdown-tree {
    grid-area: tree;
}

.dropdown-state {
    grid-area: state;
}

.dropdown-overview {
    grid-area: overview;
}
</style>
