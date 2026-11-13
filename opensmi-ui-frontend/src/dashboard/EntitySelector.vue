<script setup lang="ts">
import { computed, ref } from "vue";
import {
    PlusIcon,
    SearchIcon,
    SearchXIcon,
    XIcon,
    ChevronDownIcon,
    ChevronRightIcon,
    ChevronsDownUpIcon,
    ChevronsUpDownIcon,
    FolderIcon,
    ListIcon,
    ListPlusIcon,
    ListTreeIcon,
    TagIcon,
} from "@lucide/vue";
import { useModelStore } from "@/stores/ModelStore";
import type { ComponentNode, FeatureNode } from "@/types/NodeFeatureTypes";
import { getFeatureName, getFeatureType } from "@/dashboard/featureUtils";

type ViewMode = "list" | "tree";

interface TreeNode {
    key: string;
    label: string;
    type: string | null;
    /** Set when the node can be selected. Components, and features that are
     *  only shown because a descendant matches, have no selectable feature. */
    feature: FeatureNode | null;
    children: TreeNode[];
}

interface TreeRow {
    node: TreeNode;
    depth: number;
    expanded: boolean;
}

const props = withDefaults(
    defineProps<{
        /** Entity IDs to hide, e.g. entities that are already on the dashboard. */
        excludeIds?: string[];
        /** Maximum number of rows rendered at once (keeps huge models snappy). */
        maxRows?: number;
        /** Whether the selector starts collapsed. */
        defaultCollapsed?: boolean;
        /** Initial view mode. */
        defaultView?: ViewMode;
    }>(),
    {
        excludeIds: () => [],
        maxRows: 200,
        defaultCollapsed: false,
        defaultView: "list",
    },
);

const emit = defineEmits<{
    (e: "select", feature: FeatureNode): void;
}>();

const modelStore = useModelStore();

const collapsed = ref(props.defaultCollapsed);
const viewMode = ref<ViewMode>(props.defaultView);
const nameFilter = ref("");
const typeFilter = ref<string>("");
const expandedKeys = ref<Set<string>>(new Set());

function toggleCollapsed() {
    collapsed.value = !collapsed.value;
}

function getParentName(feature: FeatureNode): string | null {
    if (!feature.parentComponentNodeEntityId) return null;
    const parent = modelStore.entityIdComponentNodeMap.get(
        feature.parentComponentNodeEntityId,
    );
    return parent ? getFeatureName(parent) : null;
}

const excludedSet = computed(() => new Set(props.excludeIds));

const needle = computed(() => nameFilter.value.trim().toLowerCase());

const hasActiveFilter = computed(
    () => needle.value.length > 0 || typeFilter.value !== "",
);

function matchesFilter(feature: FeatureNode): boolean {
    if (typeFilter.value && getFeatureType(feature) !== typeFilter.value) {
        return false;
    }
    if (needle.value && !getFeatureName(feature).toLowerCase().includes(needle.value)) {
        return false;
    }
    return true;
}

const allFeatures = computed<FeatureNode[]>(() =>
    Array.from(modelStore.entityIdFeatureNodeMap.values()).filter(
        (f) => !excludedSet.value.has(f.entityId),
    ),
);

/** Available entity types with their counts, sorted alphabetically. */
const typeOptions = computed(() => {
    const counts = new Map<string, number>();
    for (const feature of allFeatures.value) {
        const type = getFeatureType(feature);
        counts.set(type, (counts.get(type) ?? 0) + 1);
    }
    return Array.from(counts.entries())
        .map(([type, count]) => ({ type, count }))
        .sort((a, b) => a.type.localeCompare(b.type));
});

/* ---------- Flat list ---------- */

const filteredFeatures = computed(() =>
    allFeatures.value
        .filter(matchesFilter)
        .sort((a, b) => getFeatureName(a).localeCompare(getFeatureName(b))),
);

const visibleFeatures = computed(() =>
    filteredFeatures.value.slice(0, props.maxRows),
);

/* ---------- Tree ---------- */

function buildFeatureNode(feature: FeatureNode): TreeNode | null {
    const children = feature.features
        .map(buildFeatureNode)
        .filter((n): n is TreeNode => n !== null);

    const selectable =
        !excludedSet.value.has(feature.entityId) && matchesFilter(feature);

    // Keep a node if it's selectable, or if something below it is.
    if (!selectable && children.length === 0) return null;

    return {
        key: feature.entityId,
        label: getFeatureName(feature),
        type: getFeatureType(feature),
        feature: selectable ? feature : null,
        children,
    };
}

function buildComponentNode(component: ComponentNode): TreeNode | null {
    const children = [
        ...component.children.map(buildComponentNode),
        ...component.features.map(buildFeatureNode),
    ].filter((n): n is TreeNode => n !== null);

    if (children.length === 0) return null;

    return {
        key: component.entityId,
        label: getFeatureName(component),
        type: null,
        feature: null,
        children,
    };
}

const treeRoots = computed<TreeNode[]>(() => {
    if (viewMode.value !== "tree") return [];
    return Array.from(modelStore.rootComponents.values())
        .map(buildComponentNode)
        .filter((n): n is TreeNode => n !== null);
});

/** While filtering, everything that matches is shown expanded. */
const forceOpen = computed(() => hasActiveFilter.value);

const treeRows = computed<TreeRow[]>(() => {
    const rows: TreeRow[] = [];

    function walk(nodes: TreeNode[], depth: number) {
        for (const node of nodes) {
            const expanded =
                node.children.length > 0 &&
                (forceOpen.value || expandedKeys.value.has(node.key));
            rows.push({ node, depth, expanded });
            if (expanded) walk(node.children, depth + 1);
        }
    }

    walk(treeRoots.value, 0);
    return rows;
});

const visibleTreeRows = computed(() => treeRows.value.slice(0, props.maxRows));

function toggleExpanded(key: string) {
    const next = new Set(expandedKeys.value);
    if (!next.delete(key)) next.add(key);
    expandedKeys.value = next;
}

function expandAll() {
    const keys = new Set<string>();
    function walk(nodes: TreeNode[]) {
        for (const node of nodes) {
            if (node.children.length > 0) {
                keys.add(node.key);
                walk(node.children);
            }
        }
    }
    walk(treeRoots.value);
    expandedKeys.value = keys;
}

function collapseAll() {
    expandedKeys.value = new Set();
}

function onRowClick(row: TreeRow) {
    if (row.node.feature) {
        emit("select", row.node.feature);
    } else if (row.node.children.length > 0) {
        toggleExpanded(row.node.key);
    }
}

/* ---------- Shared ---------- */

const rowCount = computed(() =>
    viewMode.value === "list"
        ? visibleFeatures.value.length
        : visibleTreeRows.value.length,
);

const isTruncated = computed(() =>
    viewMode.value === "list"
        ? filteredFeatures.value.length > visibleFeatures.value.length
        : treeRows.value.length > visibleTreeRows.value.length,
);

function resetFilters() {
    nameFilter.value = "";
    typeFilter.value = "";
}

function onSelect(feature: FeatureNode) {
    emit("select", feature);
}

function segmentClass(active: boolean) {
    return [
        "flex h-9 min-w-9 cursor-pointer items-center justify-center gap-1 rounded px-2 text-xs font-medium transition-colors duration-100 active:scale-95",
        active ? "bg-violet-200 text-violet-700" : "text-stone-500 hover:bg-stone-100",
    ];
}
</script>

<template>
    <section
        class="flex flex-col overflow-hidden rounded-md border border-stone-200 bg-white shadow-sm"
    >
        <!-- Collapse toggle / title bar -->
        <button
            type="button"
            class="flex h-12 w-full cursor-pointer items-center gap-3 bg-stone-50 px-3 text-left transition-colors duration-100 hover:bg-stone-100 active:bg-stone-200"
            :class="{ 'border-b border-stone-200': !collapsed }"
            :aria-expanded="!collapsed"
            @click="toggleCollapsed"
        >
            <ListPlusIcon
                class="size-5 shrink-0 text-stone-500"
                :stroke-width="2"
            />

            <span class="flex-1 text-sm font-semibold text-stone-700">
                Add entities
            </span>

            <span
                v-if="collapsed && hasActiveFilter"
                class="shrink-0 rounded-full border border-violet-200 bg-violet-200 px-2 py-0.5 text-xs font-medium text-violet-700"
            >
                Filtered
            </span>

            <span
                class="shrink-0 rounded-full border border-stone-200 bg-stone-100 px-2 py-0.5 text-xs font-medium text-stone-600"
            >
                {{ allFeatures.length }} available
            </span>

            <ChevronDownIcon
                class="size-5 shrink-0 text-stone-400 transition-transform duration-150"
                :class="{ '-rotate-90': collapsed }"
                :stroke-width="2"
            />
        </button>

        <template v-if="!collapsed">
            <!-- Filter bar -->
            <header
                class="flex flex-col gap-2 border-b border-stone-200 bg-stone-50 p-3 sm:flex-row"
            >
                <!-- Name filter -->
                <label class="relative flex-1">
                    <span class="sr-only">Filter by name</span>
                    <SearchIcon
                        class="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-stone-400"
                        :stroke-width="2"
                    />
                    <input
                        v-model="nameFilter"
                        type="text"
                        placeholder="Filter by name..."
                        class="h-11 w-full rounded-md border border-stone-200 bg-white pl-9 pr-9 text-sm text-stone-700 placeholder:text-stone-400 focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-200"
                    />
                    <button
                        v-if="nameFilter.length"
                        type="button"
                        aria-label="Clear name filter"
                        class="absolute right-2 top-1/2 flex size-7 -translate-y-1/2 cursor-pointer items-center justify-center rounded text-stone-400 hover:bg-stone-100 hover:text-stone-600"
                        @click="nameFilter = ''"
                    >
                        <XIcon class="size-4" :stroke-width="2" />
                    </button>
                </label>

                <!-- Type filter -->
                <label class="relative sm:w-56">
                    <span class="sr-only">Filter by entity type</span>
                    <select
                        v-model="typeFilter"
                        class="h-11 w-full cursor-pointer appearance-none rounded-md border border-stone-200 bg-white pl-3 pr-9 text-sm text-stone-700 focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-200"
                    >
                        <option value="">
                            All types ({{ allFeatures.length }})
                        </option>
                        <option
                            v-for="option in typeOptions"
                            :key="option.type"
                            :value="option.type"
                        >
                            {{ option.type }} ({{ option.count }})
                        </option>
                    </select>
                    <ChevronDownIcon
                        class="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-stone-400"
                        :stroke-width="2"
                    />
                </label>

                <!-- View mode -->
                <div
                    class="flex h-11 items-center gap-0.5 self-start rounded-md border border-stone-200 bg-white p-0.5 sm:self-auto"
                >
                    <button
                        type="button"
                        :class="segmentClass(viewMode === 'list')"
                        title="Flat list"
                        aria-label="Flat list"
                        :aria-pressed="viewMode === 'list'"
                        @click="viewMode = 'list'"
                    >
                        <ListIcon class="size-5" :stroke-width="2" />
                    </button>
                    <button
                        type="button"
                        :class="segmentClass(viewMode === 'tree')"
                        title="Tree view"
                        aria-label="Tree view"
                        :aria-pressed="viewMode === 'tree'"
                        @click="viewMode = 'tree'"
                    >
                        <ListTreeIcon class="size-5" :stroke-width="2" />
                    </button>

                    <template v-if="viewMode === 'tree' && !forceOpen">
                        <div class="mx-0.5 h-5 w-px bg-stone-200" />
                        <button
                            type="button"
                            :class="segmentClass(false)"
                            title="Expand all"
                            aria-label="Expand all"
                            @click="expandAll"
                        >
                            <ChevronsUpDownIcon class="size-5" :stroke-width="2" />
                        </button>
                        <button
                            type="button"
                            :class="segmentClass(false)"
                            title="Collapse all"
                            aria-label="Collapse all"
                            @click="collapseAll"
                        >
                            <ChevronsDownUpIcon class="size-5" :stroke-width="2" />
                        </button>
                    </template>
                </div>
            </header>

            <!-- Flat list -->
            <ul
                v-if="viewMode === 'list' && visibleFeatures.length"
                class="max-h-96 divide-y divide-stone-100 overflow-y-auto"
            >
                <li v-for="feature in visibleFeatures" :key="feature.entityId">
                    <button
                        type="button"
                        class="group flex min-h-14 w-full cursor-pointer items-center gap-3 px-3 py-2 text-left transition-colors duration-100 hover:bg-violet-50 active:bg-violet-100"
                        @click="onSelect(feature)"
                    >
                        <div class="min-w-0 flex-1">
                            <p
                                class="truncate text-sm font-semibold leading-tight text-stone-700"
                            >
                                {{ getFeatureName(feature) }}
                            </p>
                            <p
                                class="mt-0.5 truncate text-xs text-stone-400"
                                :title="getParentName(feature) ?? undefined"
                            >
                                {{
                                    getParentName(feature) ??
                                    "No parent component"
                                }}
                            </p>
                        </div>

                        <span
                            class="shrink-0 rounded-full border border-stone-200 bg-stone-100 px-2 py-0.5 text-xs font-medium text-stone-600"
                        >
                            {{ getFeatureType(feature) }}
                        </span>

                        <span
                            class="flex size-8 shrink-0 items-center justify-center rounded-md border border-stone-200 bg-stone-50 text-stone-400 transition-colors duration-100 group-hover:border-violet-200 group-hover:bg-violet-200 group-hover:text-violet-700"
                            aria-hidden="true"
                        >
                            <PlusIcon class="size-4" :stroke-width="2.5" />
                        </span>
                    </button>
                </li>
            </ul>

            <!-- Tree -->
            <ul
                v-else-if="viewMode === 'tree' && visibleTreeRows.length"
                class="max-h-96 divide-y divide-stone-100 overflow-y-auto"
                role="tree"
            >
                <li
                    v-for="row in visibleTreeRows"
                    :key="row.node.key"
                    role="treeitem"
                    :aria-expanded="
                        row.node.children.length > 0 ? row.expanded : undefined
                    "
                >
                    <div
                        class="group flex min-h-11 items-center gap-1 pr-3 transition-colors duration-100 hover:bg-violet-50"
                        :style="{ paddingLeft: `${row.depth * 16 + 8}px` }"
                    >
                        <!-- Expand / collapse -->
                        <button
                            v-if="row.node.children.length > 0"
                            type="button"
                            class="flex size-7 shrink-0 cursor-pointer items-center justify-center rounded text-stone-400 hover:bg-stone-100 hover:text-stone-600 disabled:cursor-default"
                            :disabled="forceOpen"
                            :aria-label="row.expanded ? 'Collapse' : 'Expand'"
                            @click="toggleExpanded(row.node.key)"
                        >
                            <ChevronRightIcon
                                class="size-4 transition-transform duration-150"
                                :class="{ 'rotate-90': row.expanded }"
                                :stroke-width="2"
                            />
                        </button>
                        <span v-else class="size-7 shrink-0" />

                        <!-- Main click target -->
                        <button
                            type="button"
                            class="flex min-h-11 min-w-0 flex-1 cursor-pointer items-center gap-2 text-left active:opacity-80 disabled:cursor-default"
                            :disabled="
                                !row.node.feature &&
                                row.node.children.length === 0
                            "
                            @click="onRowClick(row)"
                        >
                            <FolderIcon
                                v-if="row.node.type === null"
                                class="size-4 shrink-0 text-stone-400"
                                :stroke-width="2"
                            />
                            <TagIcon
                                v-else
                                class="size-4 shrink-0"
                                :class="
                                    row.node.feature
                                        ? 'text-violet-500'
                                        : 'text-stone-300'
                                "
                                :stroke-width="2"
                            />

                            <span
                                class="min-w-0 flex-1 truncate text-sm"
                                :class="
                                    row.node.type === null
                                        ? 'font-semibold text-stone-700'
                                        : row.node.feature
                                          ? 'text-stone-700'
                                          : 'text-stone-400'
                                "
                            >
                                {{ row.node.label }}
                            </span>

                            <span
                                v-if="row.node.type !== null"
                                class="shrink-0 rounded-full border border-stone-200 bg-stone-100 px-2 py-0.5 text-xs font-medium text-stone-600"
                            >
                                {{ row.node.type }}
                            </span>

                            <span
                                v-if="row.node.feature"
                                class="flex size-8 shrink-0 items-center justify-center rounded-md border border-stone-200 bg-stone-50 text-stone-400 transition-colors duration-100 group-hover:border-violet-200 group-hover:bg-violet-200 group-hover:text-violet-700"
                                aria-hidden="true"
                            >
                                <PlusIcon class="size-4" :stroke-width="2.5" />
                            </span>
                        </button>
                    </div>
                </li>
            </ul>

            <!-- Empty state -->
            <div
                v-else
                class="flex flex-col items-center justify-center gap-2 px-4 py-10 text-center"
            >
                <SearchXIcon
                    class="size-8 text-stone-300"
                    :stroke-width="1.75"
                />
                <p class="text-sm font-medium text-stone-500">
                    {{
                        allFeatures.length
                            ? "No entities match your filter."
                            : "No entities available."
                    }}
                </p>
                <button
                    v-if="hasActiveFilter"
                    type="button"
                    class="cursor-pointer rounded-md border border-stone-200 bg-stone-100 px-3 py-1.5 text-xs font-medium text-stone-600 hover:bg-stone-200 active:scale-95"
                    @click="resetFilters"
                >
                    Reset filters
                </button>
            </div>

            <!-- Footer -->
            <footer
                class="border-t border-stone-200 bg-stone-50 px-3 py-2 text-xs text-stone-500"
            >
                <template v-if="isTruncated">
                    Showing the first {{ rowCount }} rows. Narrow the filter to
                    see more.
                </template>
                <template v-else>
                    {{ filteredFeatures.length }} of {{ allFeatures.length }}
                    entities
                </template>
            </footer>
        </template>
    </section>
</template>
