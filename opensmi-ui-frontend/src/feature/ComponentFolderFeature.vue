<script setup lang="ts">
import type { ComponentEntityData } from "@/types/EntityTypes";
import type { ComponentNode, FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import { RouterLink } from "vue-router";
import { FolderIcon } from "@lucide/vue";

const props = defineProps<{
    feature: FeatureNode | ComponentNode; // This is fine as this "Feature" is only a stub for the Entity Page
}>();

const entity = computed(() => {
    return props.feature.entity as ComponentEntityData;
});

// First level only: children are listed, but never rendered recursively
const children = computed<ComponentNode[]>(
    () => (props.feature as ComponentNode).children ?? [],
);
</script>

<template>
    <div class="flex flex-col justify-start items-start gap-y-2 ml-1">
        <div class="flex flex-col flex-wrap justify-start items-start gap-4">
            Components
        </div>

        <!-- Direct child components (first level only), drawn as a tree -->
        <ul
            v-if="children.length"
            class="-mt-1 ml-2 flex max-w-full min-w-0 flex-col"
            aria-label="Child components"
        >
            <li v-for="child in children" :key="child.entityId">
                <RouterLink
                    :to="`/component/${encodeURIComponent(child.entityId)}`"
                    :title="child.entity.name"
                    class="flex min-w-0 max-w-full items-center gap-1.5 rounded-md px-2 py-0.5 text-sm text-emerald-400 hover:border-slate-300 hover:bg-slate-100 hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 active:bg-slate-200"
                >
                    <FolderIcon
                        :size="12"
                        :stroke-width="2"
                        class="shrink-0 text-emerald-200"
                    />
                    <span class="truncate">{{ child.entity.name }}</span>
                </RouterLink>
            </li>
        </ul>
    </div>
</template>
