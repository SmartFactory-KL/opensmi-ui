<script setup lang="ts">
import ExpectedFeature from "@/components/ExpectedFeature.vue";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import VariableContainerFeature from "@/feature/basic/VariableContainerFeature.vue";
import UserContainerFeature from "@/feature/basic/UserContainerFeature.vue";
import ResourceContainerFeature from "@/feature/basic/ResourceContainerFeature.vue";

const props = defineProps<{
    expectedFeatures: Map<string, FeatureNode> | null;
}>();
</script>

<template>
    <div
        class="flex flex-col justify-center items-stretch p-4 border-2 border-indigo-800 bg-indigo-50"
        v-if="expectedFeatures"
    >
        <div class="flex flex-row justify-around items-center gap-4">
            <ExpectedFeature
                :expected-feature="expectedFeatures.get('Identification')"
                expectedFeatureType="Identification"
                v-slot="{ feature }"
            >
                <VariableContainerFeature
                    :feature="feature"
                ></VariableContainerFeature>
            </ExpectedFeature>

            <ExpectedFeature
                :expected-feature="expectedFeatures.get('Attributes')"
                expectedFeatureType="Attributes"
                v-slot="{ feature }"
            >
                <VariableContainerFeature
                    :feature="feature"
                ></VariableContainerFeature>
            </ExpectedFeature>
        </div>
        <div class="flex flex-row justify-around items-center gap-4">
            <ExpectedFeature
                :expected-feature="expectedFeatures.get('UserContainer')"
                expectedFeatureType="UserContainer"
                v-slot="{ feature }"
            >
                <UserContainerFeature :feature="feature"></UserContainerFeature>
            </ExpectedFeature>

            <ExpectedFeature
                :expected-feature="expectedFeatures.get('ResourceContainer')"
                expectedFeatureType="ResourceContainer"
                v-slot="{ feature }"
            >
                <ResourceContainerFeature
                    :feature="feature"
                ></ResourceContainerFeature>
            </ExpectedFeature>
        </div>
    </div>
</template>
