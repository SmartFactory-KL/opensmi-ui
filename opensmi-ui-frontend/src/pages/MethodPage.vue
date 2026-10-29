<script setup lang="ts">
import EntityBreadcrumbs from "@/components/EntityBreadcrumbs.vue";
import ExpectedFeature from "@/components/ExpectedFeature.vue";
import NullablePage from "@/components/NullablePage.vue";
import MethodFeature from "@/feature/basic/MethodFeature.vue";
import VariableContainerFeature from "@/feature/basic/VariableContainerFeature.vue";
import GenericEntityPageLink from "@/link/GenericEntityPageLink.vue";
import { useModelStore } from "@/stores/ModelStore";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import { useRoute } from "vue-router";

const modelStore = useModelStore();

const route = useRoute();

const entityId = computed(() => {
    return route.params.entityId;
});

const methodFeature = computed(() => {
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

    if (methodFeature.value === null) {
        return featureMap;
    }

    for (const feature of methodFeature.value.features) {
        switch (feature.entityType) {
            case "Dependency":
                featureMap.set(feature.entityType, feature);
                break;
            case "VariableContainer":
                featureMap.set(feature.entity.name, feature);
                break;
        }
    }

    return featureMap;
});
</script>

<template>
    <NullablePage
        :item="methodFeature"
        :entityId="entityId"
        entity-type="Method"
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
                class="w-full max-w-7xl mx-auto mt-4 flex flex-col justify-start items-start gap-y-4"
            >
                <header
                    class="flex flex-row justify-between items-start w-full p-4 bg-indigo-800 text-slate-100 border-4 border-indigo-900"
                >
                    <div class="flex flex-col">
                        <span class="text-2xl">{{ item.entity.name }}</span>
                    </div>
                    <div>
                        <ExpectedFeature
                            :expected-feature="item"
                            expectedFeatureType="SkillControl"
                            v-slot="{ feature }"
                        >
                            <MethodFeature :feature="feature"></MethodFeature>
                        </ExpectedFeature>
                    </div>
                    <div class="flex flex-col gap-y-4">
                        <ExpectedFeature
                            :expected-feature="
                                expectedFeatures.get('Identification')
                            "
                            expectedFeatureType="Identification"
                            v-slot="{ feature }"
                        >
                            <VariableContainerFeature
                                :feature="feature"
                            ></VariableContainerFeature>
                        </ExpectedFeature>

                        <ExpectedFeature
                            :expected-feature="
                                expectedFeatures.get('Attributes')
                            "
                            expectedFeatureType="Attributes"
                            v-slot="{ feature }"
                        >
                            <VariableContainerFeature
                                :feature="feature"
                            ></VariableContainerFeature>
                        </ExpectedFeature>

                        <ExpectedFeature
                            :expected-feature="
                                expectedFeatures.get('Dependency')
                            "
                            expectedFeatureType="Dependency"
                            v-slot="{ feature }"
                        >
                            <DependencyFeature
                                :feature="feature"
                            ></DependencyFeature>
                        </ExpectedFeature>
                    </div>
                </header>

                <div>
                    <ExpectedFeature
                        :expected-feature="expectedFeatures.get('Monitoring')"
                        expectedFeatureType="Monitoring"
                        v-slot="{ feature }"
                    >
                        <VariableContainerFeature
                            :feature="feature"
                        ></VariableContainerFeature>
                    </ExpectedFeature>

                    <ExpectedFeature
                        :expected-feature="expectedFeatures.get('ParameterSet')"
                        expectedFeatureType="ParameterSet"
                        v-slot="{ feature }"
                    >
                        <VariableContainerFeature
                            :feature="feature"
                        ></VariableContainerFeature>
                    </ExpectedFeature>

                    <ExpectedFeature
                        :expected-feature="
                            expectedFeatures.get('FinalResultData')
                        "
                        expectedFeatureType="FinalResultData"
                        v-slot="{ feature }"
                    >
                        <VariableContainerFeature
                            :feature="feature"
                        ></VariableContainerFeature>
                    </ExpectedFeature>
                </div>

                <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
                <div class="on-screen-placeholder" style="height: 25vh"></div>
            </section>
        </main>
    </NullablePage>
</template>
