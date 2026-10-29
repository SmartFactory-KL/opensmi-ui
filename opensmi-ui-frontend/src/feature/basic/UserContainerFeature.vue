<script setup lang="ts">
import { ref, useId } from "vue";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import UserFeature from "./UserFeature.vue";
import { UsersIcon, ChevronDownIcon } from "@lucide/vue";

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
            <UsersIcon :size="16" :stroke-width="1.6" class="shrink-0" />
            <span class="font-medium">Users</span>
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
            class="grid grid-cols-[repeat(auto-fill,minmax(16rem,1fr))] gap-1.5 border-t border-gray-200 p-1.5"
        >
            <span
                v-if="!feature.features?.length"
                class="col-span-full px-1 text-xs text-stone-300"
            >
                -empty-
            </span>

            <UserFeature
                v-for="userFeature in feature.features"
                :key="userFeature.entityId"
                :feature="userFeature"
            />
        </div>
    </div>
</template>
