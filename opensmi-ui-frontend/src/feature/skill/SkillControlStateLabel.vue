<script setup lang="ts">
import type { SkillControlEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import { normalizeSkillState, type StateConfig } from "./SkillData";
import { CircleAlert } from "@lucide/vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => {
    return props.feature.entity as SkillControlEntityData;
});

const state = computed<StateConfig | null>(() => {
    const value = entity.value.currentState;
    return normalizeSkillState(value);
});

const lastChange = computed(() => {
    const value = entity.value.currentStateLastChange;

    if (!value) return "Unknown";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) return value;

    return new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(date);
});
</script>

<template>
    <div class="min-w-22">
        <p v-if="state" :class="state.iconColor">
            {{ state.label }}
        </p>
        <p v-else class="text-slate-500">
            Unknown state: {{ entity.currentState }}
        </p>
    </div>
</template>
