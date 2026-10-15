```vue
<script setup lang="ts">
import { ref, computed } from "vue";
import { AlertCircle, ChevronDown, Braces, Copy, Check } from "@lucide/vue";
import type { FeatureEntityDto } from "@/types/NodeFeatureTypes";

const props = defineProps<{
    feature: FeatureEntityDto;
}>();

const jsonExpanded = ref(false);
const copied = ref(false);

const formattedJson = computed(
    () => JSON.stringify(props.feature, null, 2) ?? "undefined",
);

async function copyJson() {
    try {
        await navigator.clipboard.writeText(formattedJson.value);
        copied.value = true;
        window.setTimeout(() => {
            copied.value = false;
        }, 1500);
    } catch {
        copied.value = false;
    }
}
</script>

<template>
    <div
        class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-md shadow-slate-200/60"
    >
        <!-- Header -->
        <div class="flex items-start gap-3 p-5">
            <div
                class="flex size-10 shrink-0 items-center justify-center rounded-lg bg-amber-50 text-amber-600"
            >
                <AlertCircle :size="20" :stroke-width="1.8" />
            </div>

            <div class="min-w-0 flex-1">
                <h3 class="text-sm font-semibold text-slate-900">
                    Unsupported Feature: {{ feature.entityType }}
                </h3>

                <p class="mt-1 text-sm leading-5 text-slate-500">
                    This feature type does not have a dedicated renderer.
                </p>
            </div>
        </div>

        <!-- JSON disclosure -->
        <div class="border-t border-slate-100">
            <button
                type="button"
                class="flex w-full items-center gap-2 px-5 py-3.5 text-left text-sm font-medium text-slate-600 hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-blue-500"
                :aria-expanded="jsonExpanded"
                @click="jsonExpanded = !jsonExpanded"
            >
                <Braces :size="17" class="shrink-0 text-slate-400" />

                <span class="flex-1">View JSON data</span>

                <ChevronDown
                    :size="17"
                    class="shrink-0 text-slate-400"
                    :class="{ 'rotate-180': jsonExpanded }"
                />
            </button>

            <div v-if="jsonExpanded" class="border-t border-slate-100">
                <div
                    class="flex items-center justify-between bg-slate-50 px-5 py-2.5"
                >
                    <span
                        class="text-xs font-medium uppercase tracking-wide text-slate-500"
                    >
                        JSON
                    </span>

                    <button
                        type="button"
                        class="inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                        @click="copyJson"
                    >
                        <Check v-if="copied" :size="14" />
                        <Copy v-else :size="14" />
                        {{ copied ? "Copied" : "Copy JSON" }}
                    </button>
                </div>

                <pre
                    class="max-h-96 overflow-auto bg-white p-5 font-mono text-xs leading-5 text-slate-700"
                ><code>{{ formattedJson }}</code></pre>
            </div>
        </div>
    </div>
</template>
```
