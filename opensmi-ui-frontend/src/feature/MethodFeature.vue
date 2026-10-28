<script setup lang="ts">
import type { SkillEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import VariableContainerFeature from "./VariableContainerFeature.vue";
import { PlayCircleIcon } from "@lucide/vue";
import IconButton from "@/components/IconButton.vue";
import Toaster from "@/toast/Toaster";
import { simplyPostToText } from "@/fetch/simplyFetch";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => props.feature.entity as SkillEntityData);

const variableContainers = computed(() => {
    const result: FeatureNode[] = [];
    for (const feature of props.feature.features) {
        if (feature.entityType === "VariableContainer") {
            result.push(feature);
        }
    }

    return result;
});

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
    <section class="bg-white text-slate-900 shadow-lg">
        <div
            class="p-2 flex flex-col justify-start items-start bg-indigo-700 text-slate-200 cursor-pointer"
            @click="$router.push('/method/' + feature.entityId)"
        >
            {{ entity.name }}
        </div>

        <div class="p-2 border-l-4 border-l-emerald-600">
            <IconButton
                @click="callMethod"
                class="bg-emerald-50 text-emerald-600"
            >
                <PlayCircleIcon></PlayCircleIcon> Call
            </IconButton>
        </div>
    </section>
</template>
