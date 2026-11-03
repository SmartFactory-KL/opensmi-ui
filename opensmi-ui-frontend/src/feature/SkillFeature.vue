<script setup lang="ts">
import type { SkillEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import SkillControlFeature from "./SkillControlFeature.vue";
import ExpectedFeature from "@/components/ExpectedFeature.vue";
import { RefreshCcw } from "@lucide/vue";

const props = defineProps<{
    feature: FeatureNode;
    name?: string;
    isContinuous?: boolean;
}>();

const entity = computed(() => props.feature.entity as SkillEntityData);

const skillControlFeature = computed(() => {
    for (const feature of props.feature.features) {
        if (feature.entityType === "SkillControl") {
            return feature;
        }
    }
    return null;
});
</script>

<template>
    <section
        class="flex flex-row justify-start items-center bg-sky-900 text-slate-200"
    >
        <div>
            <ExpectedFeature
                :expectedFeature="skillControlFeature"
                expectedFeatureType="SkillControl"
                v-slot="{ resolvedFeature }"
            >
                <SkillControlFeature
                    :feature="resolvedFeature"
                    v-if="skillControlFeature !== null"
                ></SkillControlFeature>
            </ExpectedFeature>
        </div>

        <div
            class="p-2 flex flex-col justify-between items-start cursor-pointer"
            @click="$router.push('/skill/' + feature.entityId)"
        >
            <div class="font-semibold text-sky-100 flex gap-1 items-center">
                <RefreshCcw :size="10" v-show="isContinuous"></RefreshCcw>
                {{ name?.length ? name : "Generic Skill Name" }}
            </div>
            <div
                class="bg-sky-600 text-slate-200 rounded-full px-2 py-0 text-xs"
            >
                {{ entity.name }}
            </div>
        </div>
    </section>
</template>
