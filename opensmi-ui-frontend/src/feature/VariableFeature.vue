<script setup lang="ts">
import type { VariableEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => {
    return props.feature.entity as VariableEntityData;
});

const value = computed(() => {
    if (
        typeof entity.value.value == "object" &&
        "value" in entity.value.value
    ) {
        return entity.value.value.value; // wtf
    }

    return entity.value.value;
});
</script>

<template>
    <div class="text-xs">
        {{ entity.name }} :
        <span>
            {{ value }}
        </span>
    </div>
</template>
