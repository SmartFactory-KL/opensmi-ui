<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import UnsupportedFeature from "./UnsupportedFeature.vue";
import VariableContainerFeature from "./VariableContainerFeature.vue";
import MachineryItemStateFeature from "./MachineryItemStateFeature.vue";
import UserContainerFeature from "./UserContainerFeature.vue";
import UserFeature from "./UserFeature.vue";
import VariableFeature from "./VariableFeature.vue";
import LockFeature from "./LockFeature.vue";
import SkillControlFeature from "./SkillControlFeature.vue";
import SkillFeature from "./SkillFeature.vue";
import SkillGroupFeature from "./SkillGroupFeature.vue";
import SkillSetFeature from "./SkillSetFeature.vue";
import ComponentFeature from "./ComponentFeature.vue";
import GenericEntityPageLink from "@/link/GenericEntityPageLink.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const featureComponent = computed(() => {
    switch (props.feature.entityType) {
        case "MachineryItemState":
            return MachineryItemStateFeature;

        case "Lock":
            return LockFeature;

        case "SkillGroupContainer":
            return SkillSetFeature;
        case "SkillGroup":
            return SkillGroupFeature;
        case "Skill":
            return SkillFeature;
        case "SkillControl":
            return SkillControlFeature;

        case "UserContainer":
            return UserContainerFeature;
        case "User":
            return UserFeature;

        case "VariableContainer":
            return VariableContainerFeature;
        case "Variable":
            return VariableFeature;

        // mostly exist to show something in the entity view
        case "Component":
            return ComponentFeature;

        default:
            return UnsupportedFeature;
    }
});
</script>

<template>
    <div
        class="flex flex-col justify-start items-start bg-white border border-slate-200 p-2"
    >
        <div class="flex flex-row justify-between items-center gap-x-2 mb-2">
            <div class="bg-stone-200 text-stone-600 h-6 rounded-md text-xs flex items-center px-2">
                {{ feature.entityType }}
            </div>
            <div class="uppercase font-thin">Generic Feature View</div>
            <GenericEntityPageLink
                :entity-id="feature.entityId"
                :entity-type="feature.entityType"
            ></GenericEntityPageLink>
        </div>

        <div class="text-red-800" v-show="feature.initState === 'error'">
            This feature failed to initialize due to an error:
            <div class="bg-stone-100 text-stone-800 p-4 text-xs">
                {{ feature.initError }}
            </div>
        </div>

        <component :is="featureComponent" :feature="feature"></component>
    </div>
</template>
