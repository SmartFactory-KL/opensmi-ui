<script setup lang="ts">
import MethodCallButton from "@/feature/method/MethodCallButton.vue";
import type { SkillEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";

const props = defineProps<{
  feature: FeatureNode;
}>();

const entity = computed(() => props.feature.entity as SkillEntityData);
</script>

<template>
    <section class="flex flex-row justify-start items-center gap-1">
        <MethodCallButton tiny :feature="feature"></MethodCallButton>

        <div class="text-rose-800 font-semibold cursor-pointer" @click="$router.push('/method/'+feature.entityId)">
            {{ entity.name }}
        </div>
    </section>
</template>
