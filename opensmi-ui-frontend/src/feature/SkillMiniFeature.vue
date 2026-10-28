<script setup lang="ts">
import type { SkillEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import ExpectedFeature from "@/components/ExpectedFeature.vue";
import SkillControlMiniFeature from "./SkillControlMiniFeature.vue";

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
            class="pr-2 flex flex-row justify-between items-center cursor-pointer gap-x-2"
            @click="$router.push('/skill/' + feature.entityId)"
        >
            <ExpectedFeature
                :expectedFeature="skillControlFeature"
                expectedFeatureType="SkillControl"
                v-slot="{ feature }"
            >
                <SkillControlMiniFeature
                    :feature="feature"
                    @click.stop
                    v-if="skillControlFeature !== null"
                ></SkillControlMiniFeature>
            </ExpectedFeature>

            <div class="font-normal">
                {{ name?.length ? name : "Generic Skill Name" }}
            </div>
        </div>
    </section>
</template>
