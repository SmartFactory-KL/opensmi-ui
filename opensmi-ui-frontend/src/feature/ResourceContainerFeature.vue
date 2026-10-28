<script setup lang="ts">
import { ref, useId } from "vue";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { ChevronDownIcon, PackageIcon } from "@lucide/vue";
import ResourceFeature from "./ResourceFeature.vue";

defineProps<{
    feature: FeatureNode;
}>();

const isOpen = ref(false);
const contentId = useId();
</script>

<template>
    <div class="border border-gray-300 bg-white shadow-sm">
        <!-- Header -->
        <button
            type="button"
            class="flex w-full items-center gap-x-2 px-3 py-1.5 text-left text-xs text-stone-800 transition-colors hover:bg-gray-50"
            :aria-expanded="isOpen"
            :aria-controls="contentId"
            @click="isOpen = !isOpen"
        >
            <PackageIcon :size="16" :stroke-width="1.6" class="shrink-0" />
            <span class="font-medium">Resources</span>
            <span class="text-stone-400">
                {{ feature.features?.length ?? 0 }}
            </span>
            <ChevronDownIcon
                :size="14"
                class="ml-auto shrink-0 text-stone-400 transition-transform duration-150"
                :class="isOpen ? 'rotate-0' : '-rotate-90'"
            />
        </button>

        <!-- Collapsible content -->
        <div
            v-show="isOpen"
            :id="contentId"
            class="flex flex-row gap-2"
        >
            <span
                v-if="!feature.features?.length"
                class="col-span-full px-1 text-xs text-stone-300"
            >
                -empty-
            </span>

            <ResourceFeature
                v-for="resourceFeature in feature.features"
                :key="resourceFeature.entityId"
                :feature="resourceFeature"
            />
        </div>
    </div>
</template>
