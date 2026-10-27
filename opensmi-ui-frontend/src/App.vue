<script setup lang="ts">
import { WifiOffIcon } from "@lucide/vue";
import BasicError from "./components/BasicError.vue";
import MainNavigation from "./navigation/MainNavigation.vue";
import { usePageStore } from "./stores/PageStore";
import ServerDropdown from "./navigation/ServerDropdown.vue";
import { useRoute } from "vue-router";
import { watch } from "vue";
import Toaster from "./toast/Toaster.vue";
import { useModelStore } from "./stores/ModelStore";

const pageStore = usePageStore();
const modelStore = useModelStore();

const route = useRoute();

watch(
    () => route.fullPath,
    () => {
        modelStore.closeDropdown();
    },
);
</script>

<template>
    <main class="main">
        <MainNavigation />

        <div
            class="overflow-x-auto overflow-y-auto border-t-4 border-t-emerald-800 bg-slate-50"
        >
            <!-- Request error -->
            <BasicError :error="pageStore.requestData.error"></BasicError>

            <!-- Disconnected state -->
            <div
                v-if="!pageStore.isSocketConnected"
                class="flex min-h-[calc(100vh-4rem)] items-center justify-center px-6 z-50"
            >
                <div class="flex max-w-md flex-col items-center text-center">
                    <div
                        class="mb-5 flex h-16 w-16 items-center justify-center rounded-xl bg-red-200 text-slate-500"
                    >
                        <WifiOffIcon class="h-8 w-8" stroke-width="1.75" />
                    </div>

                    <h1
                        class="text-xl font-semibold tracking-tight text-red-800"
                    >
                        Connection unavailable
                    </h1>

                    <p class="mt-2 text-sm leading-6 text-slate-500">
                        This page is currently unavailable because the
                        connection to the server has been lost. Try refreshing
                        and check if the backend is still running.
                    </p>
                </div>
            </div>

            <div v-else class="flex h-[calc(100vh-4rem-4px)]">
                <ServerDropdown
                    class="absolute top-17 w-screen h-[calc(100vh-4.25rem)] transition"
                ></ServerDropdown>

                <!-- Page content -->
                <RouterView class="h-full w-screen" :key="$route.fullPath" />

                <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
                <!-- UPDATE: Moved to the individual pages as some have different backgrounds -->
                <!-- <div class="on-screen-placeholder" style="height: 25vh"></div> -->
            </div>

            <Toaster></Toaster>
        </div>
    </main>
</template>

<style scoped>
.main {
    display: grid;
    height: 100vh;
    width: 100vw;
    grid-template-rows: 4rem 1fr;
    grid-template-columns: 1fr;
}
</style>
