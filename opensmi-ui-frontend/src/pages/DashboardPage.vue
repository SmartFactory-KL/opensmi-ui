<script setup lang="ts">
import { computed, ref } from "vue";
import {
    ArrowDownIcon,
    ArrowUpIcon,
    Columns3Icon,
    LayoutGridIcon,
    Rows3Icon,
    Trash2Icon,
} from "@lucide/vue";
import EntitySelector from "@/dashboard/EntitySelector.vue";
import DashboardElement from "@/dashboard/DashboardElement.vue";
import GenericFeature from "@/feature/GenericFeature.vue";
import {
    useDashboardStore,
    type DashboardGridSize,
    type DashboardLayout,
    type DashboardSortDirection,
    type DashboardSortKey,
} from "@/stores/DashboardStore";
import type { FeatureNode } from "@/types/NodeFeatureTypes";

const dashboardStore = useDashboardStore();

function onEntitySelected(feature: FeatureNode) {
    dashboardStore.addElement(feature);
}

const layouts: {
    value: DashboardLayout;
    label: string;
    icon: typeof Rows3Icon;
}[] = [
    { value: "rows", label: "Rows", icon: Rows3Icon },
    { value: "columns", label: "Columns", icon: Columns3Icon },
    { value: "grid", label: "Grid", icon: LayoutGridIcon },
];

const gridSizes: {
    value: DashboardGridSize;
    label: string;
    minWidth: number;
}[] = [
    { value: "small", label: "S", minWidth: 240 },
    { value: "medium", label: "M", minWidth: 340 },
    { value: "large", label: "L", minWidth: 480 },
];

// Sorting is a one-off action; we only remember the last one to toggle direction.
const lastSort = ref<{
    key: DashboardSortKey;
    direction: DashboardSortDirection;
} | null>(null);

function onSort(key: DashboardSortKey) {
    const direction: DashboardSortDirection =
        lastSort.value?.key === key && lastSort.value.direction === "asc"
            ? "desc"
            : "asc";
    lastSort.value = { key, direction };
    dashboardStore.sortElements(key, direction);
}

const containerClass = computed(() => {
    switch (dashboardStore.layout) {
        case "rows":
            return "flex flex-col gap-3";
        case "columns":
            return "flex flex-row items-start gap-3 overflow-x-auto pb-2";
        default:
            return "grid items-start gap-3";
    }
});

const containerStyle = computed(() => {
    if (dashboardStore.layout !== "grid") return undefined;
    const min = gridSizes.find(
        (s) => s.value === dashboardStore.gridSize,
    )!.minWidth;
    return {
        gridTemplateColumns: `repeat(auto-fill, minmax(min(${min}px, 100%), 1fr))`,
    };
});

const itemClass = computed(() =>
    dashboardStore.layout === "columns" ? "w-80 shrink-0 sm:w-96" : "",
);

function segmentClass(active: boolean) {
    return [
        "flex h-9 min-w-9 cursor-pointer items-center justify-center gap-1 rounded px-2 text-xs font-medium transition-colors duration-100 active:scale-95",
        active
            ? "bg-violet-200 text-violet-700"
            : "text-stone-500 hover:bg-stone-100",
    ];
}
</script>

<template>
    <main class="min-h-full bg-slate-50 p-4">
        <EntitySelector
            :exclude-ids="dashboardStore.elementIds"
            @select="onEntitySelected"
        />

        <!-- Toolbar -->
        <div
            v-if="dashboardStore.elements.length"
            class="mt-4 flex flex-wrap items-center gap-2"
        >
            <!-- Layout -->
            <div
                class="flex gap-0.5 rounded-md border border-stone-200 bg-white p-0.5 shadow-sm"
            >
                <button
                    v-for="layout in layouts"
                    :key="layout.value"
                    type="button"
                    :class="
                        segmentClass(dashboardStore.layout === layout.value)
                    "
                    :title="layout.label"
                    :aria-label="layout.label"
                    :aria-pressed="dashboardStore.layout === layout.value"
                    @click="dashboardStore.setLayout(layout.value)"
                >
                    <component
                        :is="layout.icon"
                        class="size-5"
                        :stroke-width="2"
                    />
                </button>
            </div>

            <!-- Grid size (only relevant for grid) -->
            <div
                v-if="dashboardStore.layout === 'grid'"
                class="flex gap-0.5 rounded-md border border-stone-200 bg-white p-0.5 shadow-sm"
            >
                <button
                    v-for="size in gridSizes"
                    :key="size.value"
                    type="button"
                    :class="
                        segmentClass(dashboardStore.gridSize === size.value)
                    "
                    :title="`Grid size: ${size.value}`"
                    :aria-label="`Grid size: ${size.value}`"
                    :aria-pressed="dashboardStore.gridSize === size.value"
                    @click="dashboardStore.setGridSize(size.value)"
                >
                    {{ size.label }}
                </button>
            </div>

            <!-- Sorting -->
            <div
                class="flex gap-0.5 rounded-md border border-stone-200 bg-white p-0.5 shadow-sm"
            >
                <button
                    v-for="key in ['name', 'type'] as const"
                    :key="key"
                    type="button"
                    :class="segmentClass(lastSort?.key === key)"
                    :title="`Sort by ${key}`"
                    @click="onSort(key)"
                >
                    <span class="capitalize">{{ key }}</span>
                    <template v-if="lastSort?.key === key">
                        <ArrowUpIcon
                            v-if="lastSort.direction === 'asc'"
                            class="size-3.5"
                            :stroke-width="2.5"
                        />
                        <ArrowDownIcon
                            v-else
                            class="size-3.5"
                            :stroke-width="2.5"
                        />
                    </template>
                </button>
            </div>

            <div class="flex-1" />

            <button
                type="button"
                class="flex h-9 cursor-pointer items-center gap-1.5 rounded-md border border-stone-200 bg-white px-3 text-xs font-medium text-stone-600 shadow-sm transition-colors duration-100 hover:border-rose-200 hover:bg-rose-50 hover:text-rose-600 active:scale-95"
                @click="dashboardStore.clear()"
            >
                <Trash2Icon class="size-4" :stroke-width="2" />
                Clear all
            </button>
        </div>

        <!-- Dashboard -->
        <div
            v-if="dashboardStore.elements.length"
            :class="['mt-3', containerClass]"
            :style="containerStyle"
        >
            <DashboardElement
                v-for="(feature, idx) in dashboardStore.elements"
                :key="feature.entityId"
                :class="itemClass"
                :feature="feature"
                :layout="dashboardStore.layout"
                :can-move-prev="idx > 0"
                :can-move-next="idx < dashboardStore.elements.length - 1"
                @remove="dashboardStore.removeElement(feature.entityId)"
                @move-prev="dashboardStore.moveElement(feature.entityId, -1)"
                @move-next="dashboardStore.moveElement(feature.entityId, 1)"
            >
                <GenericFeature :feature="feature" />
            </DashboardElement>
        </div>

        <p
            v-else
            class="mt-6 rounded-md border border-dashed border-stone-300 px-4 py-10 text-center text-sm text-stone-400"
        >
            The dashboard is empty. Pick an entity above to add it.
        </p>

        <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
        <div class="on-screen-placeholder" style="height: 25vh"></div>
    </main>
</template>
