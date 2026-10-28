<script setup lang="ts">
import type { DependencyEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import { ChevronRightIcon } from "@lucide/vue";
import ValueDisplayNodeId from "./valueDisplay/ValueDisplayNodeId.vue";

const props = defineProps<{
    feature: FeatureNode;
    name?: string;
}>();

const entity = computed(() => props.feature.entity as DependencyEntityData);

const dependsOn = computed(() => entity.value.dependsOn ?? []);
const dependencyOf = computed(() => entity.value.dependencyOf ?? []);

const groups = computed(() => [
    { label: "Depends on", items: dependsOn.value },
    { label: "Dependency of", items: dependencyOf.value },
]);
</script>

<template>
    <details class="group bg-indigo-800 text-slate-200 shadow-lg">
        <summary
            class="flex cursor-pointer list-none items-center gap-2 px-3 py-1.5 text-sm hover:bg-indigo-700 focus-visible:outline-2 focus-visible:outline-indigo-300 [&::-webkit-details-marker]:hidden"
        >
            <ChevronRightIcon
                class="size-4 shrink-0 text-indigo-300 transition-transform group-open:rotate-90"
                aria-hidden="true"
            />
            <span class="font-semibold">Dependencies</span>
            <span
                class="ml-auto bg-indigo-900 px-1.5 text-xs tabular-nums text-indigo-200"
                :title="`${dependsOn.length} depends on, ${dependencyOf.length} dependency of`"
            >
                {{ dependsOn.length }} / {{ dependencyOf.length }}
            </span>
        </summary>

        <div class="space-y-3 border-t border-indigo-600 px-3 py-2">
            <div v-for="group in groups" :key="group.label">
                <h4
                    class="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-300"
                >
                    {{ group.label }}
                    <span class="font-normal tabular-nums text-indigo-400">
                        ({{ group.items.length }})
                    </span>
                </h4>

                <div v-if="group.items.length" class="space-y-0.5 text-sm">
                    <div v-for="nodeId in group.items" :key="String(nodeId)">
                        <ValueDisplayNodeId :value="nodeId"></ValueDisplayNodeId>
                    </div>
                </div>
                <div v-else class="text-xs italic text-indigo-400">None</div>
            </div>
        </div>
    </details>
</template>
