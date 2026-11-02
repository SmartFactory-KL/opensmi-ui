<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { LayoutGridIcon, ListIcon } from "@lucide/vue";
import { computed, ref } from "vue";
import VariableFeature from "./VariableFeature.vue";

defineProps<{
    feature: FeatureNode;
}>();

type ViewMode = "list" | "grid";
type GridSize = "sm" | "md" | "lg" | "xl";

// Minimum column width per size; the grid fits as many columns as possible
const gridSizes: { key: GridSize; label: string; minWidth: string }[] = [
    { key: "sm", label: "S", minWidth: "10rem" },
    { key: "md", label: "M", minWidth: "14rem" },
    { key: "lg", label: "L", minWidth: "20rem" },
    { key: "xl", label: "XL", minWidth: "28rem" },
];

const viewMode = ref<ViewMode>("list");
const gridSize = ref<GridSize>("md");

// Tailwind can't generate classes from runtime values, so this one is an inline style
const gridStyle = computed(() => {
    const size = gridSizes.find((s) => s.key === gridSize.value);
    return {
        gridTemplateColumns: `repeat(auto-fill, minmax(min(${size?.minWidth ?? "14rem"}, 100%), 1fr))`,
    };
});
</script>

<template>
    <div class="flex flex-col w-full">
        <div
            class="flex flex-row justify-between items-center gap-4 border-l-4 border-l-slate-600 bg-indigo-100 px-4"
        >
            <span>{{ feature.entity.name }}</span>

            <div class="inline-flex items-center gap-2">
                <!-- Grid size selector, only relevant in grid view -->
                <div
                    v-if="viewMode === 'grid'"
                    class="inline-flex items-center"
                    role="group"
                    aria-label="Grid size"
                >
                    <button
                        v-for="size in gridSizes"
                        :key="size.key"
                        type="button"
                        :title="`Grid size ${size.label}`"
                        :aria-pressed="gridSize === size.key"
                        @click="gridSize = size.key"
                        :class="
                            gridSize === size.key
                                ? 'bg-slate-600 text-slate-100'
                                : 'text-slate-600 hover:bg-indigo-200'
                        "
                        class="px-1.5 py-0.5 text-xs font-medium cursor-pointer active:scale-95"
                    >
                        {{ size.label }}
                    </button>
                </div>

                <!-- View mode toggle -->
                <div class="inline-flex items-center" role="group">
                    <button
                        type="button"
                        title="List view"
                        aria-label="List view"
                        :aria-pressed="viewMode === 'list'"
                        @click="viewMode = 'list'"
                        :class="
                            viewMode === 'list'
                                ? 'bg-slate-600 text-slate-100'
                                : 'text-slate-600 hover:bg-indigo-200'
                        "
                        class="p-1 cursor-pointer active:scale-95"
                    >
                        <ListIcon :size="16"></ListIcon>
                    </button>

                    <button
                        type="button"
                        title="Grid view"
                        aria-label="Grid view"
                        :aria-pressed="viewMode === 'grid'"
                        @click="viewMode = 'grid'"
                        :class="
                            viewMode === 'grid'
                                ? 'bg-slate-600 text-slate-100'
                                : 'text-slate-600 hover:bg-indigo-200'
                        "
                        class="p-1 cursor-pointer active:scale-95"
                    >
                        <LayoutGridIcon :size="16"></LayoutGridIcon>
                    </button>
                </div>
            </div>
        </div>

        <div
            :class="
                viewMode === 'grid'
                    ? 'grid gap-2 p-2'
                    : 'flex flex-col justify-start items-stretch'
            "
            :style="viewMode === 'grid' ? gridStyle : undefined"
        >
            <span
                class="text-xs"
                :class="{ 'col-span-full': viewMode === 'grid' }"
                v-show="feature.features?.length == 0"
                >-empty-</span
            >

            <VariableFeature
                v-for="variableFeature in feature.features"
                :key="variableFeature.entityId"
                :feature="variableFeature"
            >
            </VariableFeature>
        </div>
    </div>
</template>
