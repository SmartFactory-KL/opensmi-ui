<script setup lang="ts">
import EntityBreadcrumbs from "@/components/EntityBreadcrumbs.vue";
import ExpectedFeature from "@/components/ExpectedFeature.vue";
import NullablePage from "@/components/NullablePage.vue";
import DependencyFeature from "@/feature/DependencyFeature.vue";
import SkillControlFeature from "@/feature/SkillControlFeature.vue";
import SkillFeature from "@/feature/SkillFeature.vue";
import VariableContainerFeature from "@/feature/VariableContainerFeature.vue";
import GenericEntityPageLink from "@/link/GenericEntityPageLink.vue";
import { useModelStore } from "@/stores/ModelStore";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { ChevronLeftIcon, ChevronRightIcon } from "@lucide/vue";
import { computed, ref } from "vue";
import { useRoute } from "vue-router";

const modelStore = useModelStore();

const route = useRoute();

const entityId = computed(() => {
    return route.params.entityId;
});

const skillFeature = computed(() => {
    const _entityId = entityId.value;

    if (!_entityId || Array.isArray(_entityId)) {
        console.log("invalid component entity id:", _entityId);
        return null;
    }

    if (!modelStore.entityIdFeatureNodeMap.has(_entityId)) {
        return null;
    }

    return modelStore.entityIdFeatureNodeMap.get(_entityId) ?? null;
});

const expectedFeatures = computed<Map<string, FeatureNode | null>>(() => {
    const featureMap = new Map<string, FeatureNode>();

    if (skillFeature.value === null) {
        return featureMap;
    }

    for (const feature of skillFeature.value.features) {
        switch (feature.entityType) {
            case "Dependency":
            case "SkillControl":
                featureMap.set(feature.entityType, feature);
                break;
            case "VariableContainer":
                featureMap.set(feature.entity.name, feature);
                break;
        }
    }

    return featureMap;
});

const skillGroupLabel = computed(() => {
    const parentFeatureEntityId = skillFeature.value?.parentFeatureNodeEntityId;

    if (!parentFeatureEntityId) {
        return "Unknown Name";
    }

    const parentFeature = modelStore.entityIdFeatureNodeMap.get(
        parentFeatureEntityId,
    );

    return parentFeature?.entity?.name || "Unknown name";
});

type PanelKey = "identification-attributes";

// Only one panel can be open at a time
const activePanel = ref<PanelKey | null>(null);

function togglePanel(panel: PanelKey) {
    activePanel.value = activePanel.value === panel ? null : panel;
}
</script>

<template>
    <NullablePage
        :item="skillFeature"
        :entityId="entityId"
        entity-type="SkillGroup"
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
                    class="sticky top-8 w-64 h-[calc(100vh-6rem-4px)] shrink-0 overflow-y-auto flex flex-col justify-start items-stretch p-4 bg-sky-800 text-slate-100 border-r-2 border-sky-900 gap-2"
                >
                    <div class="flex flex-col">
                        <span class="text-2xl">{{ skillGroupLabel }}</span>
                        <span class="text-xs">{{ item.entity.name }}</span>
                    </div>

                    <!-- Pushes the buttons to the bottom of the sidebar -->
                    <div class="grow"></div>

                    <div class="flex flex-col justify-start items-end gap-1">
                        <button
                            type="button"
                            @click="togglePanel('identification-attributes')"
                            :class="
                                activePanel === 'identification-attributes'
                                    ? 'text-sky-100 bg-sky-600 border-sky-300'
                                    : 'text-sky-700 bg-sky-300'
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
                    </div>
                </header>

                <section
                    class="w-full flex flex-col justify-start items-stretch gap-3 pl-4 pr-4 pt-4"
                >
                    <div class="flex flex-row justify-center items-center">
                        <div class="bg-sky-800 p-5">
                            <ExpectedFeature
                                :expected-feature="skillFeature"
                                expectedFeatureType="Skill"
                                v-slot="{ resolvedFeature }"
                            >
                                <SkillFeature
                                    :feature="resolvedFeature"
                                ></SkillFeature>
                            </ExpectedFeature>
                        </div>
                    </div>

                    <section class="flex flex-row justify-around gap-8">
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

                            <ExpectedFeature
                                :expected-feature="
                                    expectedFeatures.get('FinalResultData')
                                "
                                expectedFeatureType="FinalResultData"
                                v-slot="{ resolvedFeature }"
                            >
                                <VariableContainerFeature
                                    :feature="resolvedFeature"
                                ></VariableContainerFeature>
                            </ExpectedFeature>
                        </div>

                        <div
                            class="flex flex-col justify-start items-start gap-4"
                        >
                            <ExpectedFeature
                                :expected-feature="
                                    expectedFeatures.get('Dependency')
                                "
                                expectedFeatureType="Dependency"
                                v-slot="{ resolvedFeature }"
                            >
                                <DependencyFeature
                                    :feature="resolvedFeature"
                                ></DependencyFeature>
                            </ExpectedFeature>
                        </div>
                    </section>

                    <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
                    <div
                        class="on-screen-placeholder"
                        style="height: 25vh"
                    ></div>

                    <!-- Inlay panel: sits directly to the right of the sidebar, one panel at a time -->
                    <section
                        v-if="activePanel"
                        class="fixed bottom-0 left-64 w-[calc(100vw-16rem)] bg-sky-200 border-t-2 border-emerald-900 shadow-lg text-xs"
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
