<script setup lang="ts">
import type { SkillEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import { PlayCircleIcon } from "@lucide/vue";
import IconButton from "@/components/IconButton.vue";
import Toaster from "@/toast/Toaster";
import { simplyPostToText } from "@/fetch/simplyFetch";

const props = defineProps<{
    feature: FeatureNode;
    tiny?: boolean;
}>();

const entity = computed(() => props.feature.entity as SkillEntityData);

async function callMethod() {
    try {
        const action = {
            entityId: props.feature.entityId,
            actionType: "MethodCall",
            action: {},
        };

        await simplyPostToText("/api/opc-model/action", action);

        Toaster.success("Method called successfully");
    } catch (e) {
        console.error(e);
        Toaster.error("Failed to call method: " + e);
    }
}
</script>

<template>
    <button
        type="button"
        @click="callMethod"
        class="bg-emerald-50 text-emerald-600 flex justify-center items-center text-sm cursor-pointer active:scale-95"
        :class="[tiny ? 'size-8 border' : 'border-2 gap-2 px-2 py-1']"
    >
        <PlayCircleIcon :class="[tiny ? 'size-6' : 'size-8']"></PlayCircleIcon>
        <span v-show="!tiny">Call</span>
    </button>
</template>
