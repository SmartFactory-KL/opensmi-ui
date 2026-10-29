<script setup lang="ts">
import EntityBreadcrumbs from "@/components/EntityBreadcrumbs.vue";
import ExpectedFeature from "@/components/ExpectedFeature.vue";
import IconButton from "@/components/IconButton.vue";
import NullablePage from "@/components/NullablePage.vue";
import ComponentAdditionalInformation from "@/feature/ComponentAdditionalInformation.vue";
import ComponentFolderFeature from "@/feature/ComponentFolderFeature.vue";
import ComponentTitleFeature from "@/feature/ComponentTitleFeature.vue";
import LockFeature from "@/feature/basic/LockFeature.vue";
import MachineryItemStateFeature from "@/feature/basic/MachineryItemStateFeature.vue";
import MethodContainerFeature from "@/feature/basic/MethodContainerFeature.vue";
import SkillGroupContainerFeature from "@/feature/basic/SkillGroupContainerFeature.vue";
import VariableContainerFeature from "@/feature/basic/VariableContainerFeature.vue";
import GenericEntityPageLink from "@/link/GenericEntityPageLink.vue";
import { useModelStore } from "@/stores/ModelStore";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { ChevronDownIcon, ChevronUpIcon } from "@lucide/vue";
import { computed, ref } from "vue";
import { useRoute } from "vue-router";

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

const showDetails = ref(false);
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
                    class="sticky top-8 min-w-[20vw] h-[calc(100vh-6rem-4px)] overflow-y-auto flex flex-col justify-start items-start p-4 bg-emerald-800 text-slate-100 border-r-2 border-emerald-900 gap-2"
                >
                    <ComponentTitleFeature
                        :feature="item"
                    ></ComponentTitleFeature>

                    <ExpectedFeature
                        :expected-feature="
                            expectedFeatures.get('MachineryItemState')
                        "
                        expectedFeatureType="MachineryItemState"
                        optional
                        v-slot="{ feature }"
                    >
                        <MachineryItemStateFeature
                            :feature="feature"
                        ></MachineryItemStateFeature>
                    </ExpectedFeature>

                    <ExpectedFeature
                        :expected-feature="expectedFeatures.get('Lock')"
                        expectedFeatureType="Lock"
                        optional
                        v-slot="{ feature }"
                    >
                        <LockFeature :feature="feature"></LockFeature>
                    </ExpectedFeature>

                    <ComponentFolderFeature
                        :feature="item"
                    ></ComponentFolderFeature>
                </header>

                <section
                    class="w-full flex flex-col justify-start items-stretch gap-3 pl-4 pr-4 pt-4"
                >
                    <div class="flex flex-col justify-end items-end">
                        <div>
                            <IconButton
                                @click="showDetails = !showDetails"
                                class="bg-indigo-50 border-indigo-800"
                            >
                                Attributes | Users | Resources
                                <ChevronDownIcon
                                    v-show="!showDetails"
                                ></ChevronDownIcon>
                                <ChevronUpIcon
                                    v-show="showDetails"
                                ></ChevronUpIcon>
                            </IconButton>
                        </div>

                        <ComponentAdditionalInformation
                            :expectedFeatures="expectedFeatures"
                            v-show="showDetails"
                            class="mt-2 w-full"
                        ></ComponentAdditionalInformation>
                    </div>

                    <section class="flex flex-row justify-around">
                        <div
                            class="flex flex-col justify-start items-start gap-8"
                        >
                            <ExpectedFeature
                                :expected-feature="
                                    expectedFeatures.get('Monitoring')
                                "
                                expectedFeatureType="Monitoring"
                                v-slot="{ feature }"
                            >
                                <VariableContainerFeature
                                    :feature="feature"
                                ></VariableContainerFeature>
                            </ExpectedFeature>

                            <ExpectedFeature
                                :expected-feature="
                                    expectedFeatures.get('ParameterSet')
                                "
                                expectedFeatureType="ParameterSet"
                                v-slot="{ feature }"
                            >
                                <VariableContainerFeature
                                    :feature="feature"
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
                                v-slot="{ feature }"
                            >
                                <SkillGroupContainerFeature
                                    :feature="feature"
                                ></SkillGroupContainerFeature>
                            </ExpectedFeature>

                            <ExpectedFeature
                                :expected-feature="
                                    expectedFeatures.get('MethodContainer')
                                "
                                optional
                                expectedFeatureType="MethodContainer"
                                v-slot="{ feature }"
                            >
                                <MethodContainerFeature
                                    :feature="feature"
                                ></MethodContainerFeature>
                            </ExpectedFeature>
                        </div>
                    </section>
                    <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
                    <div
                        class="on-screen-placeholder"
                        style="height: 25vh"
                    ></div>
                </section>
            </section>
        </main>
    </NullablePage>
</template>
