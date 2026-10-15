<script setup lang="ts">
import type { FeatureEntityDto } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import UnsupportedFeature from "./UnsupportedFeature.vue";
import AttributesFeature from "./AttributesFeature.vue";
import IdentificationFeature from "./IdentificationFeature.vue";
import MonitoringFeature from "./MonitoringFeature.vue";
import ParameterFeature from "./ParameterFeature.vue";
import RemoteLockFeature from "./RemoteLockFeature.vue";

const props = defineProps<{
    feature: FeatureEntityDto;
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
        <component :is="featureComponent" :feature="feature"></component>
    </div>
</template>
