<script setup lang="ts">
import EntityBreadcrumbs from "@/components/EntityBreadcrumbs.vue";
import ExpectedFeature from "@/components/ExpectedFeature.vue";
import NullablePage from "@/components/NullablePage.vue";
import ComponentFeature from "@/feature/ComponentFeature.vue";
import LockFeature from "@/feature/LockFeature.vue";
import MethodContainerFeature from "@/feature/MethodContainerFeature.vue";
import SkillGroupContainerFeature from "@/feature/SkillGroupContainerFeature.vue";
import UserContainerFeature from "@/feature/UserContainerFeature.vue";
import VariableContainerFeature from "@/feature/VariableContainerFeature.vue";
import GenericEntityPageLink from "@/link/GenericEntityPageLink.vue";
import { useModelStore } from "@/stores/ModelStore";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
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

const expectedFeatures = computed<Map<string, FeatureNode | null>>(() => {
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
                class="w-full max-w-7xl mx-auto mt-4 flex flex-col justify-start items-start gap-y-4"
            >
                <header
                    class="flex flex-row justify-between items-start w-full p-4 bg-emerald-800 text-slate-100 border-4 border-emerald-900"
                >
                    <div class="flex flex-col">
                        <ComponentFeature :feature="item"></ComponentFeature>
                    </div>
                    <div>
                        <ExpectedFeature
                            :expected-feature="expectedFeatures.get('Lock')"
                            expectedFeatureType="Lock"
                            optional
                            v-slot="{ feature }"
                        >
                            <LockFeature :feature="feature"></LockFeature>
                        </ExpectedFeature>
                    </div>
                    <div class="flex flex-col gap-y-4">
                        <ExpectedFeature
                            :expected-feature="
                                expectedFeatures.get('Identification')
                            "
                            expectedFeatureType="Identification"
                            optional
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
                                expectedFeatures.get('UserContainer')
                            "
                            expectedFeatureType="UserContainer"
                            optional
                            v-slot="{ feature }"
                        >
                            <UserContainerFeature
                                :feature="feature"
                            ></UserContainerFeature>
                        </ExpectedFeature>
                    </div>
                </header>

                <div class="flex flex-row"></div>

                <div class="flex flex-row justify-center gap-x-4">
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
                </div>

                <div>
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
                </div>

                <div>
                    <ExpectedFeature
                        :expected-feature="
                            expectedFeatures.get('MethodContainer')
                        "
                        expectedFeatureType="MethodContainer"
                        v-slot="{ feature }"
                    >
                        <MethodContainerFeature
                            :feature="feature"
                        ></MethodContainerFeature>
                    </ExpectedFeature>
                </div>
                <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
                <div class="on-screen-placeholder" style="height: 25vh"></div>
            </section>
        </main>
    </NullablePage>
</template>
