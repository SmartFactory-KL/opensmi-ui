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

        default:
            return UnsupportedFeature;
    }
});
</script>

<template>
    <div>
        <div class="text-red-800" v-show="feature.initState === 'error'">
            This feature failed to initialize due to an error:
            <div class="bg-stone-100 text-stone-800 p-4 text-xs">
                {{ feature.initError }}
            </div>
        </div>
        <component :is="featureComponent" :feature="feature"></component>
    </div>
</template>
