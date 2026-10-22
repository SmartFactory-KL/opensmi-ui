<script setup lang="ts">
import type { UserEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import { ShieldCheck, CircleCheck, CircleX, LockKeyhole } from "@lucide/vue";

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
        class="w-full shadow-sm max-w-64 border border-gray-200 bg-white p-4 text-gray-900 transition-colors hover:border-gray-300"
    >
        <!-- Header -->
        <div class="flex items-start gap-3">
            <div class="min-w-0 flex-1">
                <h3 class="truncate text-sm font-semibold tracking-tight">
                    {{ entity.name || "Unnamed user" }}
                </h3>

                <div class="mt-1 flex items-center gap-1.5">
                    <span
                        class="size-2 rounded-full"
                        :class="isPresent ? 'bg-emerald-500' : 'bg-gray-300'"
                    />

                    <span class="text-xs text-gray-500">
                        {{ isPresent ? "Present" : "Not present" }}
                    </span>
                </div>
            </div>

            <span
                v-if="allowsMultiple"
                class="inline-flex shrink-0 items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium"
                :class="
                    allowsMultiple
                        ? 'bg-emerald-50 text-emerald-700'
                        : 'bg-gray-100 text-gray-500'
                "
            >
                <CircleCheck :size="13" /> Multi-User
            </span>
        </div>

        <!-- Access information -->
        <div class="mt-5 border-t border-gray-100 pt-4">
            <div class="mb-3 flex items-center justify-between gap-4">
                <span
                    class="flex items-center gap-2 text-xs font-medium text-gray-500"
                >
                    <ShieldCheck :size="15" />
                    Current access
                </span>

                <span class="text-right text-sm font-semibold text-gray-900">
                    {{ accessLevel }}
                </span>
            </div>

            <div class="flex items-center justify-between gap-4">
                <span
                    class="flex items-center gap-2 text-xs font-medium text-gray-500"
                >
                    <LockKeyhole :size="15" />
                    Maximum access
                </span>

                <span class="text-right text-sm font-medium text-gray-700">
                    {{ maxAccessLevel }}
                </span>
            </div>
        </div>
    </article>
</template>
