```vue
<script setup lang="ts">
import { WifiOffIcon } from "@lucide/vue";
import BasicError from "./components/BasicError.vue";
import MainNavigation from "./navigation/MainNavigation.vue";
import { usePageStore } from "./stores/PageStore";

const pageStore = usePageStore();
</script>

<template>
    <main class="main">
        <MainNavigation />

        <div
            class="overflow-x-auto overflow-y-scroll border-t-4 border-t-slate-500 bg-slate-50"
        >
            <!-- Request error -->
            <BasicError :error="pageStore.requestData.error"></BasicError>

            <!-- Disconnected state -->
            <div
                v-if="!pageStore.isSocketConnected"
                class="flex min-h-[calc(100vh-4rem)] items-center justify-center px-6"
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
                        connection to the server has been lost. Try refreshing and check if the backend is still running.
                    </p>
                </div>
            </div>

            <!-- Page content -->
            <RouterView v-else :key="$route.fullPath" />

            <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
            <div class="on-screen-placeholder" style="height: 25vh"></div>
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
```
