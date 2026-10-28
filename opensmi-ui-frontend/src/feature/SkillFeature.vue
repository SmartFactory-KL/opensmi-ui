<script setup lang="ts">
import type { SkillEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import SkillControlFeature from "./SkillControlFeature.vue";
import ExpectedFeature from "@/components/ExpectedFeature.vue";

const props = defineProps<{
    feature: FeatureNode;
    name?: string;
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
    <section class="bg-sky-800 text-slate-200 shadow-lg">
        <div
            class="p-2 flex flex-row justify-between items-center cursor-pointer"
            @click="$router.push('/skill/' + feature.entityId)"
        >
            <div class="font-normal">
                {{ name?.length ? name : "Generic Skill Name" }}
            </div>
            <div
                class="bg-sky-950 text-slate-300 rounded-full px-2 py-0 text-xs"
            >
                {{ entity.name }}
            </div>
        </div>

        <div>
            <ExpectedFeature
                :expectedFeature="skillControlFeature"
                expectedFeatureType="SkillControl"
                v-slot="{ feature }"
            >
                <SkillControlFeature
                    :feature="feature"
                    v-if="skillControlFeature !== null"
                ></SkillControlFeature>
            </ExpectedFeature>
        </div>
    </section>
</template>
