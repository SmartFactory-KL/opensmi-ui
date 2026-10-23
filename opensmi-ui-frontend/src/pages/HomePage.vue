<script setup lang="ts">
import { usePageStore } from "@/stores/PageStore";
import { ArrowRightIcon, LinkIcon, ShieldCheckIcon } from "@lucide/vue";
import { useRouter } from "vue-router";

const pageStore = usePageStore();
const router = useRouter();
</script>

<template>
    <main>
        <div class="mx-auto w-full flex max-w-6xl flex-col px-6 py-12 lg:px-8">
            <!-- Hero -->
            <section class="flex flex-1 flex-col justify-center py-16">
                <div class="max-w-3xl">
                    <!-- Welcome -->
                    <h1
                        class="text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl"
                    >
                        Welcome to
                        <span class="text-slate-500">OpenSMI UI</span>
                    </h1>

                    <p class="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
                        Explore and interact with your machines through the
                        standardized OpenSMI OPC UA interface. Browse the
                        machine hierarchy, monitor live data, and discover
                        available skills and capabilities.
                    </p>

                    <!-- Primary actions -->
                    <div class="mt-9 flex flex-wrap gap-3">
                        <button
                            class="group inline-flex items-center gap-2 rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 cursor-pointer"
                            @click="router.push('/connect')"
                        >
                            <LinkIcon :size="18" />
                            Establish Connection
                            <ArrowRightIcon
                                :size="16"
                                class="transition-transform group-hover:translate-x-0.5"
                            />
                        </button>
                    </div>
                </div>
            </section>

            <!-- Footer -->
            <footer
                class="flex items-center justify-between pt-8 text-xs text-slate-400"
            >
                <div class="flex items-center gap-2">
                    <ShieldCheckIcon :size="14" />
                    OPC UA
                </div>

                <span>
                    OpenSMI UI Version
                    {{ pageStore.pageSettings.appVersion }}</span
                >
            </footer>
        </div>

        <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
        <div class="on-screen-placeholder" style="height: 25vh"></div>
    </main>
</template>
