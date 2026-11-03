<script setup lang="ts">
import ExpectedFeature from "@/components/ExpectedFeature.vue";
import MiniMethodContainer from "@/components/MiniMethodContainer.vue";
import MiniSkillContainer from "@/components/MiniSkillContainer.vue";
import ComponentTypeBadge from "@/feature/component/ComponentTypeBadge.vue";
import GenericFeature from "@/feature/GenericFeature.vue";
import MethodContainerFeature from "@/feature/MethodContainerFeature.vue";
import SkillGroupContainerFeature from "@/feature/SkillGroupContainerFeature.vue";
import SkillGroupFeature from "@/feature/SkillGroupFeature.vue";
import ComponentLink from "@/link/ComponentLink.vue";
import type { ComponentNode, FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";

const props = defineProps<{
    component: ComponentNode;
}>();

const hasChildElements = computed(() => {
    return props.component?.children?.length;
});

const expectedFeatures = computed(() => {
    const result = new Map<string, FeatureNode>();

    for (const child of props.component.features) {
        switch (child.entityType) {
            case "SkillGroupContainer":
            case "MethodContainer":
                result.set(child.entityType, child);
        }
    }

    return result;
});
</script>

<template>
    <div>
        <div
            class="flex flex-row justify-between items-center bg-emerald-800 h-10 px-2"
        >
            <ComponentLink :component="component"></ComponentLink>

            <ComponentTypeBadge :feature="component"></ComponentTypeBadge>
        </div>
        <div
            class="text-xs ml-4 border-l-4 px-4 py-2 border-l-emerald-800 bg-slate-200"
        >
            <div class="flex flex-row justify-start gap-x-4">
                <div class="flex-1 min-w-0">
                    <ExpectedFeature
                        :expectedFeature="
                            expectedFeatures.get('SkillGroupContainer')
                        "
                        expectedFeatureType="SkillGroupContainer"
                        optional
                        v-slot="{ resolvedFeature }"
                    >
                        <MiniSkillContainer
                            :feature="resolvedFeature"
                        ></MiniSkillContainer>
                    </ExpectedFeature>
                </div>

                <div class="flex-1 min-w-0">
                    <ExpectedFeature
                        :expectedFeature="
                            expectedFeatures.get('MethodContainer')
                        "
                        expectedFeatureType="MethodContainer"
                        optional
                        v-slot="{ resolvedFeature }"
                    >
                        <MiniMethodContainer
                            :feature="resolvedFeature"
                        ></MiniMethodContainer>
                    </ExpectedFeature>
                </div>
            </div>
        </div>
        <div v-if="hasChildElements" class="ml-4">
            <ComponentTreeElement
                :component="childComponent"
                v-for="childComponent in component.children"
            ></ComponentTreeElement>
        </div>
    </div>
</template>
