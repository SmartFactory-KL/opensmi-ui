<script setup lang="ts">
import type { VariableEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import FeatureErrorWrapper from "./FeatureErrorWrapper.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => {
    return props.feature.entity as VariableEntityData;
});

const value = computed(() => {
    if (
        entity !== null &&
        entity.value !== null &&
        entity.value.value !== null &&
        typeof entity.value.value == "object" &&
        "value" in entity.value.value
    ) {
        return entity.value.value.value; // wtf
    }

    return entity.value.value;
});
</script>

<template>
    <FeatureErrorWrapper :feature="feature">
        <div class="text-xs">
            {{ entity.name }} :
            <span>
                {{ value }}
            </span>
        </div>
    </FeatureErrorWrapper>
</template>
