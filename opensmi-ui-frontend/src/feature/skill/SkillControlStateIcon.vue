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
  return normalizeSkillState(value)
});
</script>

<template>
    <div
        class="flex size-9 shrink-0 items-center justify-center rounded-full border"
        :class="state ? state.color : 'border-slate-200 bg-slate-50'"
    >
        <component
            :is="state ? state.icon : CircleAlert"
            class="size-5"
            :class="
                state
                    ? [
                          state.iconColor,
                          state.isBusy &&
                              'animate-spin motion-reduce:animate-none',
                      ]
                    : 'text-slate-500'
            "
            :aria-label="state?.label ?? 'Unknown state'"
        />
    </div>
</template>
