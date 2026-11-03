<script setup lang="ts">
import EntityBreadcrumbs from "@/components/EntityBreadcrumbs.vue";
import ExpectedFeature from "@/components/ExpectedFeature.vue";
import NullablePage from "@/components/NullablePage.vue";
import ComponentFolders from "@/feature/component/ComponentFolders.vue";
import ComponentTitle from "@/feature/component/ComponentTitle.vue";

import LockFeature from "@/feature/LockFeature.vue";
import MachineryItemStateFeature from "@/feature/MachineryItemStateFeature.vue";
import MethodContainerFeature from "@/feature/MethodContainerFeature.vue";
import SkillGroupContainerFeature from "@/feature/SkillGroupContainerFeature.vue";
import VariableContainerFeature from "@/feature/VariableContainerFeature.vue";
import UserContainerFeature from "@/feature/UserContainerFeature.vue";
import ResourceContainerFeature from "@/feature/ResourceContainerFeature.vue";
import GenericEntityPageLink from "@/link/GenericEntityPageLink.vue";
import { useModelStore } from "@/stores/ModelStore";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { ChevronLeftIcon, ChevronRightIcon } from "@lucide/vue";
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import ComponentTypeBadge from "@/feature/component/ComponentTypeBadge.vue";
import MiniSkillContainer from "@/components/MiniSkillContainer.vue";
import MiniMethodContainer from "@/components/MiniMethodContainer.vue";

const modelStore = useModelStore();

const route = useRoute();

const entityId = computed(() => {
    return route.params.entityId;
});

const component = computed(() => {
    const _entityId = entityId.value;

    if (!_entityId || Array.isArray(_entityId)) {
        console.log("invalid component entity id:", _entityId);
        return null;
    }

    if (!modelStore.entityIdComponentNodeMap.has(_entityId)) {
        return null;
    }

    return modelStore.entityIdComponentNodeMap.get(_entityId) ?? null;
});

const expectedFeatures = computed<Map<string, FeatureNode>>(() => {
    const featureMap = new Map<string, FeatureNode>();

    if (component.value === null) {
        return featureMap;
    }

    for (const feature of component.value.features) {
        switch (feature.entityType) {
            case "MachineryItemState":
            case "UserContainer":
            case "SkillGroupContainer":
            case "MethodContainer":
            case "ResourceContainer":
            case "Lock":
                featureMap.set(feature.entityType, feature);
                break;
            case "VariableContainer":
                featureMap.set(feature.entity.name, feature);
                break;
        }
    }

    return featureMap;
});

type PanelKey = "identification-attributes" | "users-resources";

// Only one panel can be open at a time
const activePanel = ref<PanelKey | null>(null);

function togglePanel(panel: PanelKey) {
    activePanel.value = activePanel.value === panel ? null : panel;
}
</script>

<template>
    <NullablePage
        :item="component"
        :entityId="entityId"
        entity-type="Component"
        v-slot="{ item }"
    >
        <main class="w-full flex flex-col justify-start items-start">
            <div
                class="sticky top-0 flex flex-row justify-between items-center w-full bg-slate-200 pr-4 pl-2"
            >
                <EntityBreadcrumbs
                    :node="item"
                    class="grow h-8"
                ></EntityBreadcrumbs>

                <GenericEntityPageLink
                    tiny
                    :entityId="entityId"
                ></GenericEntityPageLink>
            </div>

            <section
                class="w-full mx-auto flex flex-row justify-start items-stretch gap-y-4"
            >
                <header
                    class="sticky top-8 w-64 h-[calc(100vh-6rem-4px)] shrink-0  overflow-y-auto flex flex-col justify-start items-stretch p-4 bg-emerald-800 text-slate-100 border-r-2 border-emerald-900 gap-2"
                >
                    <div class="flex items-start justify-start">
                        <ComponentTypeBadge
                            :feature="item"
                        ></ComponentTypeBadge>
                    </div>

                    <ExpectedFeature
                        :expected-feature="
                            expectedFeatures.get('MachineryItemState')
                        "
                        expectedFeatureType="MachineryItemState"
                        optional
                        v-slot="{ resolvedFeature }"
                    >
                        <MachineryItemStateFeature
                            :feature="resolvedFeature"
                        ></MachineryItemStateFeature>
                    </ExpectedFeature>

                    <ComponentTitle :feature="item"></ComponentTitle>

                    <ExpectedFeature
                        :expected-feature="expectedFeatures.get('Lock')"
                        expectedFeatureType="Lock"
                        optional
                        v-slot="{ resolvedFeature }"
                    >
                        <LockFeature
                            dark
                            :feature="resolvedFeature"
                        ></LockFeature>
                    </ExpectedFeature>

                    <ComponentFolders
                        :feature="item"
                        class="grow overflow-auto mt-2"
                    ></ComponentFolders>

                    <div class="flex flex-col justify-start items-end gap-1">
                        <button
                            type="button"
                            @click="togglePanel('identification-attributes')"
                            :class="
                                activePanel === 'identification-attributes'
                                    ? 'text-emerald-100 bg-emerald-600 border-emerald-300'
                                    : 'text-emerald-700 bg-emerald-300'
                            "
                            class="inline-flex items-center gap-1 px-2 py-1 text-xs border-2 cursor-pointer active:scale-95"
                        >
                            Identification | Attributes
                            <ChevronRightIcon
                                v-show="
                                    activePanel !== 'identification-attributes'
                                "
                            ></ChevronRightIcon>
                            <ChevronLeftIcon
                                v-show="
                                    activePanel === 'identification-attributes'
                                "
                            ></ChevronLeftIcon>
                        </button>

                        <button
                            type="button"
                            @click="togglePanel('users-resources')"
                            v-if="
                                expectedFeatures.has('UserContainer') ||
                                expectedFeatures.has('ResourceContainer')
                            "
                            :class="
                                activePanel === 'users-resources'
                                    ? 'text-emerald-100 bg-emerald-600 border-emerald-300'
                                    : 'text-emerald-700 bg-emerald-300'
                            "
                            class="inline-flex items-center gap-1 px-2 py-1 text-xs border-2 cursor-pointer active:scale-95"
                        >
                            Users | Resources
                            <ChevronRightIcon
                                v-show="activePanel !== 'users-resources'"
                            ></ChevronRightIcon>
                            <ChevronLeftIcon
                                v-show="activePanel === 'users-resources'"
                            ></ChevronLeftIcon>
                        </button>
                    </div>
                </header>

                <section
                    class="w-full flex flex-col justify-start items-stretch gap-3 pl-4 pr-4 pt-4"
                >
                    <section class="flex flex-row justify-around">
                        <div
                            class="flex flex-col justify-start items-stretch gap-8"
                        >
                            <ExpectedFeature
                                :expected-feature="
                                    expectedFeatures.get('Monitoring')
                                "
                                expectedFeatureType="Monitoring"
                                v-slot="{ resolvedFeature }"
                            >
                                <VariableContainerFeature
                                    :feature="resolvedFeature"
                                ></VariableContainerFeature>
                            </ExpectedFeature>

                            <ExpectedFeature
                                :expected-feature="
                                    expectedFeatures.get('ParameterSet')
                                "
                                expectedFeatureType="ParameterSet"
                                v-slot="{ resolvedFeature }"
                            >
                                <VariableContainerFeature
                                    :feature="resolvedFeature"
                                ></VariableContainerFeature>
                            </ExpectedFeature>
                        </div>

                        <div
                            class="flex flex-col jusitfy-start items-start gap-4"
                        >
                            <ExpectedFeature
                                :expected-feature="
                                    expectedFeatures.get('SkillGroupContainer')
                                "
                                expectedFeatureType="SkillGroupContainer"
                                v-slot="{ resolvedFeature }"
                            >
                                <MiniSkillContainer
                                    :feature="resolvedFeature"
                                ></MiniSkillContainer>
                            </ExpectedFeature>

                            <ExpectedFeature
                                :expected-feature="
                                    expectedFeatures.get('MethodContainer')
                                "
                                optional
                                expectedFeatureType="MethodContainer"
                                v-slot="{ resolvedFeature }"
                            >
                                <MiniMethodContainer
                                    :feature="resolvedFeature"
                                ></MiniMethodContainer>
                            </ExpectedFeature>
                        </div>
                    </section>
                    <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
                    <div
                        class="on-screen-placeholder"
                        style="height: 25vh"
                    ></div>

                    <!-- On Screen Inlays for Identification/Attributes and Users/Resources -->
                    <!-- Inlay panel: sits directly to the right of the sidebar, one panel at a time -->
                    <section
                        v-if="activePanel"
                        class="fixed bottom-0 left-64 w-[calc(100%-16rem)] bg-emerald-200 border-t-2 border-emerald-900 shadow-lg text-xs"
                    >
                        <div
                            v-if="activePanel === 'identification-attributes'"
                            class="grid grid-cols-2 items-start gap-4 p-4"
                        >
                            <div class="min-w-0">
                                <ExpectedFeature
                                    :expected-feature="
                                        expectedFeatures.get('Identification')
                                    "
                                    expectedFeatureType="Identification"
                                    v-slot="{ resolvedFeature }"
                                >
                                    <VariableContainerFeature
                                        :feature="resolvedFeature"
                                    ></VariableContainerFeature>
                                </ExpectedFeature>
                            </div>

                            <div class="min-w-0">
                                <ExpectedFeature
                                    :expected-feature="
                                        expectedFeatures.get('Attributes')
                                    "
                                    expectedFeatureType="Attributes"
                                    v-slot="{ resolvedFeature }"
                                >
                                    <VariableContainerFeature
                                        :feature="resolvedFeature"
                                    ></VariableContainerFeature>
                                </ExpectedFeature>
                            </div>
                        </div>

                        <div
                            v-else-if="activePanel === 'users-resources'"
                            class="grid grid-cols-2 items-start gap-4 p-4"
                        >
                            <div class="min-w-0">
                                <ExpectedFeature
                                    :expected-feature="
                                        expectedFeatures.get('UserContainer')
                                    "
                                    expectedFeatureType="UserContainer"
                                    v-slot="{ resolvedFeature }"
                                >
                                    <UserContainerFeature
                                        :feature="resolvedFeature"
                                    ></UserContainerFeature>
                                </ExpectedFeature>
                            </div>

                            <div class="min-w-0">
                                <ExpectedFeature
                                    :expected-feature="
                                        expectedFeatures.get(
                                            'ResourceContainer',
                                        )
                                    "
                                    expectedFeatureType="ResourceContainer"
                                    v-slot="{ resolvedFeature }"
                                >
                                    <ResourceContainerFeature
                                        :feature="resolvedFeature"
                                    ></ResourceContainerFeature>
                                </ExpectedFeature>
                            </div>
                        </div>

                        <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
                        <div
                            class="on-screen-placeholder"
                            style="height: 25vh"
                        ></div>
                    </section>
                </section>
            </section>
        </main>
    </NullablePage>
</template>
