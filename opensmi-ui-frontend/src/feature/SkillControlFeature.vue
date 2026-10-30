<script setup lang="ts">
import { computed } from "vue";

import type { SkillControlEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";

import SkillControlStateIcon from "./skill/SkillControlStateIcon.vue";
import SkillControlStateLabel from "./skill/SkillControlStateLabel.vue";
import SkillControlButtons from "./skill/SkillControlButtons.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => props.feature.entity as SkillControlEntityData);
</script>

<template>
    <section
        class="w-full bg-white text-slate-900"
        :aria-label="`${entity.name} state`"
    >
        <div class="flex items-stretch">
            <div class="flex min-w-0 flex-1 items-center gap-2.5 px-3 py-2">
                <!-- State icon -->
                <SkillControlStateIcon
                    :feature="feature"
                ></SkillControlStateIcon>

                <!-- Name, state, last change -->
                <SkillControlStateLabel
                    :feature="feature"
                ></SkillControlStateLabel>

                <!-- Controls pill, upper right corner -->
                <SkillControlButtons :feature="feature"></SkillControlButtons>
            </div>
        </div>
    </section>
</template>
