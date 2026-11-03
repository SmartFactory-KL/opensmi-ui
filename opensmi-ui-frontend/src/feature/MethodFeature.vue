<script setup lang="ts">
import type { SkillEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import { PlayCircleIcon } from "@lucide/vue";
import IconButton from "@/components/IconButton.vue";
import Toaster from "@/toast/Toaster";
import { simplyPostToText } from "@/fetch/simplyFetch";
import MethodCallButton from "./method/MethodCallButton.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => props.feature.entity as SkillEntityData);
</script>

<template>
    <section class="bg-white text-slate-900 shadow-lg">
        <div
            class="p-2 flex flex-col justify-start items-start bg-rose-800 text-slate-200 cursor-pointer"
            @click="$router.push('/method/' + feature.entityId)"
        >
            {{ entity.name }}
        </div>

        <MethodCallButton :feature="feature"></MethodCallButton>
    </section>
</template>
