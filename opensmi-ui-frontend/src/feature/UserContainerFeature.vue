<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import UserFeature from "./UserFeature.vue";
import { UsersIcon } from "@lucide/vue";

defineProps<{
    feature: FeatureNode;
}>();
</script>

<template>
    <div
        class="border border-gray-300 p-4 shadow-sm bg-white flex flex-col gap-y-1"
    >
        <div class="text-stone-800 text-xs flex flex-row justify-start items-center gap-x-2">
            <UsersIcon></UsersIcon> {{ feature.entity.name }}
        </div>
        <div class="flex flex-row flex-wrap gap-2 justify-start items-start">
            <span
                class="text-stone-300 text-xs"
                v-show="feature.features?.length == 0"
                >-empty-</span
            >

            <UserFeature
                v-for="variableFeature in feature.features"
                :key="variableFeature.entityId"
                class="p-0.5 text-sm"
                :feature="variableFeature"
            >
            </UserFeature>
        </div>
    </div>
</template>
