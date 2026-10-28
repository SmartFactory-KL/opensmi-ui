<script setup lang="ts">
import ExpectedFeature from "@/components/ExpectedFeature.vue";
import GenericFeature from "@/feature/GenericFeature.vue";
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
        <div class="flex flex-row justify-start items-center">
            <ComponentLink class="w-full" :component="component"></ComponentLink>
        </div>
        <div class="text-xs ml-4">
            <div>
                <ExpectedFeature
                    :expectedFeature="
                        expectedFeatures.get('SkillGroupContainer')
                    "
                    v-slot="{ feature }"
                >
                    <SkillGroupContainerFeature
                        tiny
                        asColumn
                        :feature="feature"
                    ></SkillGroupContainerFeature>
                </ExpectedFeature>
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
