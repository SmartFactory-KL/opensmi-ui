<script setup lang="ts">
import { useModelStore } from "@/stores/ModelStore";
import MachineComponentTree from "@/tree/ComponentTree.vue";
import ServerStateIndicator from "./ServerStateIndicator.vue";
import MachineOverviewCard from "./DropdownMachineOverviewCard.vue";
import QuickConnectButton from "./QuickConnectButton.vue";
import IconButton from "@/components/IconButton.vue";
import { RefreshCcwDotIcon, WorkflowIcon } from "@lucide/vue";
import { useServerStore } from "@/stores/ServerSessionStore";

const modelStore = useModelStore();
const serverStore = useServerStore();
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
            v-show="modelStore.isDropdownVisible"
            class="flex items-start px-24 pt-3 bg-slate-900/80 z-10"
            @click.self.prevent="modelStore.closeDropdown()"
        >
            <div
                class="z-20 w-full overflow-hidden bg-slate-800 shadow-2xl rounded-3xl"
            >
                <!-- Inner Part -->
                <div class="my-4 max-h-[calc(80vh-2rem)] overflow-y-auto px-4">
                    <div class="flex flex-row justify-between">
                        <div
                            class="flex flex-col justify-start items-start max-w-96 min-w-96"
                        >
                            <!-- State and Connection Stuff -->
                            <div
                                class="w-full flex flex-col gap-4 justify-center items-center"
                            >
                                <!-- Current state -->
                                <ServerStateIndicator
                                    @click="modelStore.closeDropdown()"
                                ></ServerStateIndicator>

                                <!-- Controls -->
                                <div
                                    class="flex flex-row justify-around w-full"
                                >
                                    <!-- Connect/Disconnect -->
                                    <QuickConnectButton></QuickConnectButton>

                                    <!-- Browse/Load -->
                                    <IconButton
                                        class="bg-slate-700 hover:bg-slate-800 text-white"
                                        @click="modelStore.requestBrowsing()"
                                        :disabled="
                                            serverStore.isDisconnected ||
                                            modelStore.isWorking
                                        "
                                    >
                                        <WorkflowIcon
                                            :size="16"
                                            :class="{
                                                'animate-spin':
                                                    modelStore.isWorking,
                                            }"
                                        />
                                        Browse
                                    </IconButton>

                                    <IconButton
                                        class="bg-slate-700 hover:bg-slate-800 text-white"
                                        @click="modelStore.loadModel()"
                                        :disabled="
                                            serverStore.isDisconnected ||
                                            modelStore.isWorking
                                        "
                                    >
                                        <RefreshCcwDotIcon
                                            :size="16"
                                            :class="{
                                                'animate-spin':
                                                    modelStore.isWorking,
                                            }"
                                        />
                                        Load Model
                                    </IconButton>
                                </div>
                            </div>

                            <!-- Root Component and Locking Overview -->
                            <div
                                class="w-full mt-4 flex flex-col justify-start items-stretch gap-4"
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

                                <section
                                    class="flex flex-col justify-start items-stretch gap-8"
                                >
                                    <MachineOverviewCard
                                        v-for="component in modelStore.rootComponents.values()"
                                        :key="component.entityId"
                                        :component="component"
                                        :active="
                                            modelStore.currentMachine ==
                                            component
                                        "
                                        :class="{
                                            'machine-tab-active':
                                                modelStore.currentMachine ==
                                                component,
                                        }"
                                        @click="
                                            modelStore.currentMachine =
                                                component
                                        "
                                        class="cursor-pointer rounded-l-xl"
                                    ></MachineOverviewCard>
                                </section>
                            </div>
                        </div>
                        <!-- Root Component Trees -->
                        <div class="grow bg-slate-300 rounded-xl pl-4 pt-4 pr-0 pb-10">
                            <div class="overflow-auto max-h-[calc(80vh-4rem)] pr-4">
                                <span
                                    v-show="modelStore.isWorking"
                                    class="text-center text-pink-500 text-xs"
                                >
                                    Laden...
                                </span>
                                <div
                                    v-if="modelStore.currentMachine"
                                    class="mb-4 pl-2 pt-2"
                                >
                                    <MachineComponentTree
                                        :component="modelStore.currentMachine"
                                    ></MachineComponentTree>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </Transition>
</template>

<style scoped>
.machine-tab-active {
    --join-radius: 0.75rem;
    --join-color: var(
        --color-slate-300,
        #cbd5e1
    ); /* must match the panel's bg */
    position: relative;
}

.machine-tab-active::before,
.machine-tab-active::after {
    content: "";
    position: absolute;
    right: 0;
    width: var(--join-radius);
    height: var(--join-radius);
    pointer-events: none;
}

/* curve above the card */
.machine-tab-active::before {
    top: calc(var(--join-radius) * -1);
    background: radial-gradient(
        circle at top left,
        transparent calc(var(--join-radius) - 0.5px),
        var(--join-color) var(--join-radius)
    );
}

/* curve below the card */
.machine-tab-active::after {
    bottom: calc(var(--join-radius) * -1);
    background: radial-gradient(
        circle at bottom left,
        transparent calc(var(--join-radius) - 0.5px),
        var(--join-color) var(--join-radius)
    );
}
</style>
