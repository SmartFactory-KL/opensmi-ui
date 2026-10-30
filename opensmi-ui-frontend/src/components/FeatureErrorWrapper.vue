<script setup lang="ts">
import { computed, ref, toRaw } from "vue";
import {
    CheckIcon,
    ChevronRightIcon,
    CopyIcon,
    TriangleAlertIcon,
} from "@lucide/vue";
import type { FeatureNode } from "@/types/NodeFeatureTypes";

const props = defineProps<{
    feature: FeatureNode;
}>();

const failed = computed(() => props.feature.initState !== "done");

const errorText = computed(() => {
    const err = props.feature.initError;
    if (err === null || err === undefined || err === "") return null;
    return typeof err === "string" ? err : JSON.stringify(err, null, 2);
});

const snapshot = JSON.stringify(toRaw(props.feature), null, 2);

const lineCount = computed(() => snapshot.split("\n").length);

const copied = ref(false);

async function copySnapshot() {
    try {
        await navigator.clipboard.writeText(snapshot);
        copied.value = true;
        setTimeout(() => (copied.value = false), 1500);
    } catch (e) {
        console.error(e);
    }
}

const isEntityOk = computed(() => {
    return props.feature.entity !== null;
});
</script>

<template>
    <!-- Error state -->
    <section v-if="failed" role="alert">
        <header class="flex items-stretch border-b border-red-300 bg-red-50">
            <div
                class="flex w-12 shrink-0 items-center justify-center bg-red-600 text-white"
            >
                <TriangleAlertIcon class="size-5" aria-hidden="true" />
            </div>
            <div class="min-w-0 flex-1 px-3 py-2">
                <h3 class="text-sm font-semibold leading-tight text-red-900">
                    Feature not in state done but in {{ feature.initState }}
                </h3>
                <div class="text-slate-800 text-xs">
                    {{ feature.entityType }}
                </div>
            </div>
        </header>

        <dl class="text-xs">
            <dd
                v-if="errorText"
                class="max-h-40 overflow-auto whitespace-pre-wrap wrap-break-words border border-red-200 bg-red-50 px-2 py-1.5 font-mono text-red-800"
            >
                {{ errorText }}
            </dd>
            <dd v-else class="mt-0.5 text-slate-400">
                No error message provided
            </dd>
        </dl>

        <!-- JSON snapshot -->
        <details class="group border-t border-slate-300">
            <summary
                class="flex cursor-pointer list-none items-center gap-2 bg-slate-50 px-3 py-1 text-xs hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-indigo-500 [&::-webkit-details-marker]:hidden"
            >
                <ChevronRightIcon
                    class="size-3.5 shrink-0 text-slate-500 group-open:rotate-90"
                    aria-hidden="true"
                />
                <span class="font-semibold text-slate-700">JSON snapshot</span>
                <span
                    class="bg-slate-200 px-1 text-center tabular-nums text-slate-600"
                >
                    {{ lineCount }} lines
                </span>
            </summary>

            <div class="border-t border-slate-200">
                <div
                    class="flex items-center justify-end border-b border-slate-200 bg-white px-2 py-0.5"
                >
                    <button
                        type="button"
                        class="flex items-center gap-1 px-1.5 py-0.5 text-xs text-slate-500 hover:bg-slate-100 hover:text-slate-800 focus-visible:outline-2 focus-visible:outline-indigo-500"
                        @click="copySnapshot"
                    >
                        <CheckIcon
                            v-if="copied"
                            class="size-3.5 text-emerald-600"
                        />
                        <CopyIcon v-else class="size-3.5" />
                        {{ copied ? "Copied" : "Copy" }}
                    </button>
                </div>
                <pre
                    class="max-h-96 overflow-auto bg-slate-50 px-3 py-2 font-mono text-xs leading-relaxed text-slate-800"
                    >{{ snapshot }}</pre
                >
            </div>
        </details>
    </section>

    <!-- Normal state -->
    <div v-else class="contents">
        <div v-if="!isEntityOk">
            This feature has a Null Entity!
        </div>
        <slot v-else :feature="feature" />
    </div>
</template>
