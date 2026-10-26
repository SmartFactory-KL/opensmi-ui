<script setup lang="ts">
import { computed } from "vue";
import {
    BoxIcon,
    ChevronRightIcon,
    ComponentIcon,
    Feather,
    FeatherIcon,
    PuzzleIcon,
    RatIcon,
} from "@lucide/vue";

import { useModelStore } from "@/stores/ModelStore";
import type { ComponentNode, FeatureNode } from "@/types/NodeFeatureTypes";

const props = defineProps<{
    node: FeatureNode | ComponentNode;
}>();

const modelStore = useModelStore();

type Crumb = { id: string; label: string };

function isFeatureNode(node: FeatureNode | ComponentNode): node is FeatureNode {
    return "parentFeatureNodeEntityId" in node;
}

function labelOf(
    node: FeatureNode | ComponentNode | undefined,
    id: string,
): string {
    return node?.opcNode?.displayName?.text || id.slice(0, 8);
}

// Component ancestors, root first. For a feature this is its containing
// component and that component's parents; for a component, its parents.
const componentTrail = computed<Crumb[]>(() => {
    const trail: Crumb[] = [];
    const visited = new Set<string>([props.node.entityId]);
    let id = props.node.parentComponentNodeEntityId;

    while (id && !visited.has(id)) {
        visited.add(id);
        const component = modelStore.entityIdComponentNodeMap.get(id);
        trail.unshift({ id, label: labelOf(component, id) });
        id = component?.parentComponentNodeEntityId ?? null;
    }

    return trail;
});

// Feature ancestors, root first. Empty for components.
const featureTrail = computed<Crumb[]>(() => {
    const trail: Crumb[] = [];
    const visited = new Set<string>([props.node.entityId]);
    let current: FeatureNode | ComponentNode | undefined = props.node;

    while (
        current &&
        isFeatureNode(current) &&
        current.parentFeatureNodeEntityId
    ) {
        const id: string = current.parentFeatureNodeEntityId;
        if (visited.has(id)) break;
        visited.add(id);

        const parent = modelStore.entityIdFeatureNodeMap.get(id);
        trail.unshift({ id, label: labelOf(parent, id) });
        current = parent;
    }

    return trail;
});

const currentLabel = computed(() => labelOf(props.node, props.node.entityId));
const nodeIsFeature = computed(() => isFeatureNode(props.node));
</script>

<template>
    <nav
        aria-label="Breadcrumb"
        class="flex flex-row gap-x-1 items-center text-xs"
    >
        <div class="ml-1 mr-1">
            <RatIcon :size="14" class="text-pink-400"></RatIcon>
        </div>

        <!-- Component -->
        <ol class="flex min-w-0 flex-wrap items-center gap-x-2">
            <li
                v-for="(crumb, index) in componentTrail"
                :key="crumb.id"
                class="flex min-w-0 items-center gap-1"
            >
                <RouterLink
                    :to="`/component/${crumb.id}`"
                    class="inline-flex max-w-48 items-center gap-1 rounded-md border border-sky-200 bg-sky-50 px-2 py-0.5 text-sky-700 hover:border-sky-400"
                    :title="`${crumb.label}`"
                >
                    <ComponentIcon
                        class="size-3.5 shrink-0"
                        aria-hidden="true"
                    />
                    <span class="truncate">{{ crumb.label }}</span>
                </RouterLink>

                <ChevronRightIcon
                    class="size-4 shrink-0 text-sky-300"
                    aria-hidden="true"
                />
            </li>

            <li v-if="!nodeIsFeature" class="min-w-0" aria-current="page">
                <span class="truncate font-semibold text-slate-700">
                    {{ currentLabel }}
                </span>
            </li>
        </ol>

        <!-- Features -->
        <ol v-if="nodeIsFeature" class="flex min-w-0 flex-wrap items-center">
            <li
                v-for="(crumb, index) in featureTrail"
                :key="crumb.id"
                class="flex min-w-0 items-center gap-1"
            >
                <RouterLink
                    :to="`/entity/${crumb.id}`"
                    class="inline-flex max-w-48 items-center gap-1 rounded-md border border-sky-200 bg-sky-50 px-2 py-0.5 text-sky-700 transition hover:border-sky-300 hover:bg-sky-100 hover:text-sky-800 focus-visible:outline-2 focus-visible:outline-sky-500"
                    :title="`${crumb.label}`"
                >
                    <FeatherIcon class="size-3.5 shrink-0" aria-hidden="true" />
                    <span class="truncate">{{ crumb.label }}</span>
                </RouterLink>

                <ChevronRightIcon
                    class="size-4 shrink-0 text-sky-300"
                    aria-hidden="true"
                />
            </li>

            <li class="min-w-0" aria-current="page">
                <span class="truncate font-semibold text-slate-700">
                    {{ currentLabel }}
                </span>
            </li>
        </ol>
    </nav>
</template>
