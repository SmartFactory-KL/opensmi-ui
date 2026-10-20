<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import UnsupportedFeature from "./UnsupportedFeature.vue";
import AttributesFeature from "./AttributesFeature.vue";
import IdentificationFeature from "./IdentificationFeature.vue";
import MonitoringFeature from "./MonitoringFeature.vue";
import ParameterFeature from "./ParameterFeature.vue";
import RemoteLockFeature from "./RemoteLockFeature.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const featureComponent = computed(() => {
    switch (props.feature.entityType) {
        case "Attributes":
            return AttributesFeature;
        case "Identification":
            return IdentificationFeature;
        case "Monitoring":
            return MonitoringFeature;
        case "ParameterSet":
            return ParameterFeature;

        case "RemoteLock":
            return RemoteLockFeature;

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
