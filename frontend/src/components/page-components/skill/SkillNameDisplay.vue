<script lang="ts" setup>
import { computed } from 'vue';

const props = defineProps<{
  skill: SkillDto;
}>();

const isExecSkill = computed(() => {
  return props.skill?.nodeId.endsWith("SkillExecution") || false;
});

const isFC = computed(() => {
  return props.skill?.nodeId.endsWith("FeasibilityCheck") || false;
});

const isPC = computed(() => {
  return props.skill?.nodeId.endsWith("PreconditionCheck") || false;
});
</script>

<template>
  <span v-show="!isExecSkill">
    <span v-show="isFC" class="text-violet-400" title="FeasibilityCheck">FC</span>
    <span v-show="isPC" class="text-pink-400" title="PreconditionCheck">PC</span>
  </span>
  {{ skill.name }}
</template>

<style scoped></style>
