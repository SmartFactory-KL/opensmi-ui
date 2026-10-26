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
    <section class="border border-slate-200 bg-white text-slate-900 shadow-lg">
        <div class="p-2 text-xs flex flex-col justify-start items-start">
            <div>Name: {{ entity.name }}</div>
            <div>Minimum Access Level: {{ entity.minAccessLevel }}</div>
        </div>

        <div class="p-2">
            <IconButton @click="callMethod">
                <PlayCircleIcon></PlayCircleIcon> Call
            </IconButton>
        </div>

        <VariableContainerFeature
            v-for="container in variableContainers"
            :key="container.entityId"
            :feature="container"
        ></VariableContainerFeature>
    </section>
</template>
