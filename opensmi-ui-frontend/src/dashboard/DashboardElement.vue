<script setup lang="ts">
import {
    ArrowDownIcon,
    ArrowLeftIcon,
    ArrowRightIcon,
    ArrowUpIcon,
    XIcon,
} from "@lucide/vue";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import type { DashboardLayout } from "@/stores/DashboardStore";
import { getFeatureName, getFeatureType } from "@/dashboard/featureUtils";

defineProps<{
    feature: FeatureNode;
    layout: DashboardLayout;
    canMovePrev: boolean;
    canMoveNext: boolean;
}>();

defineEmits<{
    (e: "remove"): void;
    (e: "move-prev"): void;
    (e: "move-next"): void;
}>();

const iconButton =
    "flex size-7 shrink-0 cursor-pointer items-center justify-center rounded text-stone-400 transition-colors duration-100 hover:bg-stone-100 hover:text-stone-600 active:scale-95 disabled:cursor-default disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-stone-400";
</script>

<template>
    <article class="flex min-w-0 flex-col rounded-md border border-stone-200 bg-white">
        <header class="flex items-center gap-1 border-b border-stone-200 bg-stone-50 px-2 py-1.5">
            <div class="min-w-0 flex-1 px-1">
                <p class="truncate text-sm font-semibold leading-tight text-stone-700">
                    {{ getFeatureName(feature) }}
                </p>
                <p class="truncate text-xs text-stone-400">
                    {{ getFeatureType(feature) }}
                </p>
            </div>

            <!-- Rows move vertically, columns and grid move horizontally -->
            <button
                type="button"
                :class="iconButton"
                :disabled="!canMovePrev"
                :aria-label="layout === 'rows' ? 'Move up' : 'Move earlier'"
                :title="layout === 'rows' ? 'Move up' : 'Move earlier'"
                @click="$emit('move-prev')"
            >
                <ArrowUpIcon v-if="layout === 'rows'" class="size-4" :stroke-width="2" />
                <ArrowLeftIcon v-else class="size-4" :stroke-width="2" />
            </button>
            <button
                type="button"
                :class="iconButton"
                :disabled="!canMoveNext"
                :aria-label="layout === 'rows' ? 'Move down' : 'Move later'"
                :title="layout === 'rows' ? 'Move down' : 'Move later'"
                @click="$emit('move-next')"
            >
                <ArrowDownIcon v-if="layout === 'rows'" class="size-4" :stroke-width="2" />
                <ArrowRightIcon v-else class="size-4" :stroke-width="2" />
            </button>

            <button
                type="button"
                :class="[iconButton, 'hover:bg-rose-100 hover:text-rose-600']"
                aria-label="Remove from dashboard"
                title="Remove from dashboard"
                @click="$emit('remove')"
            >
                <XIcon class="size-4" :stroke-width="2" />
            </button>
        </header>

        <div class="min-w-0 p-3">
            <slot />
        </div>
    </article>
</template>
