<script setup lang="ts">
import type { SkillEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import ExpectedFeature from "@/components/ExpectedFeature.vue";
import { RefreshCcw } from "@lucide/vue";
import SkillControlStateIcon from "@/feature/skill/SkillControlStateIcon.vue";
import SkillControlButtons from "@/feature/skill/SkillControlButtons.vue";

const props = defineProps<{
    feature: FeatureNode;
    name?: string;
    isGroup?: boolean;
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
    <section class="flex flex-row justify-start items-center gap-1">
        <ExpectedFeature
            :expectedFeature="skillControlFeature"
            expectedFeatureType="SkillControl"
            v-slot="{ resolvedFeature }"
        >
            <SkillControlStateIcon
                tiny
                :feature="resolvedFeature"
            ></SkillControlStateIcon>

            <SkillControlButtons
                tiny
                :feature="resolvedFeature"
            ></SkillControlButtons>

            <div
                class="flex flex-row justify-start gap-1 items-center cursor-pointer"
                @click="$router.push('/skill/' + feature.entityId)"
            >
                <RefreshCcw :size="10" v-show="isContinuous"></RefreshCcw>
                <div class="text-sky-800 font-semibold">{{ name }}</div>
                <div
                    v-show="isGroup"
                    class="bg-slate-100 px-1 py-0.5 text-xs rounded-full text-stone-600"
                >
                    {{ entity.name }}
                </div>
            </div>
        </ExpectedFeature>
    </section>
</template>
