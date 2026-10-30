<script setup lang="ts">
import type { UserEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import { ShieldCheck, LockKeyhole } from "@lucide/vue";
import AllowMultipleIcon from "@/components/AllowMultipleIcon.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => props.feature.entity as UserEntityData);

const isPresent = computed(() => entity.value.isPresent);
const allowsMultiple = computed(() => entity.value.allowMultiple === true);

const accessLevel = computed(() => entity.value.currentAccessLevel);
const maxAccessLevel = computed(() => entity.value.maxAccessLevel);
</script>

<template>
    <article
        class="flex w-full items-center gap-3 border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-900 shadow-sm transition-colors hover:border-gray-300"
    >
        <!-- Presence + name -->
        <div class="flex min-w-0 flex-1 items-center gap-3">
            <!-- Multi-user indicator with check / cross badge -->
            <AllowMultipleIcon
                :allows-multiple="allowsMultiple"
            ></AllowMultipleIcon>

            <!-- is present -->
            <span
                class="size-2 shrink-0 rounded-full"
                :class="isPresent ? 'bg-emerald-500' : 'bg-gray-300'"
                :title="isPresent ? 'Present' : 'Not present'"
            />

            <!-- name -->
            <span
                class="truncate font-semibold tracking-tight grow"
                :title="entity.name"
            >
                {{ entity.name || "Unnamed user" }}
            </span>
        </div>

        <!-- Access info -->
        <div class="flex shrink-0 items-center gap-3 text-xs text-gray-500">
            <span class="flex items-center gap-1" title="Current access">
                <ShieldCheck :size="14" />
                <span class="font-semibold text-gray-900">
                    {{ accessLevel }}
                </span>
            </span>

            <span class="flex items-center gap-1" title="Maximum access">
                <LockKeyhole :size="14" />
                <span class="font-medium text-gray-700">
                    {{ maxAccessLevel }}
                </span>
            </span>
        </div>
    </article>
</template>
