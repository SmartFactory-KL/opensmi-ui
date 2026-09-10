<script lang="ts" setup>
import GenericStateDisplay from "../../GenericStateDisplay.vue";
import SkillNameDisplay from "./SkillNameDisplay.vue";

defineProps<{
  skill: SkillDto | undefined;
  minimal?: boolean;
  nodeId?: string;
}>();
</script>

<template>
  <div class="skill-link">
    <RouterLink
      v-if="skill"
      class="machine-link"
      :to="'/skill/' + skill.entityId"
    >
      <i
        class="fa-solid fa-rotate fa-xs w-3 basis-3 shrink-0"
        v-if="skill.type == 'Continuous'"
      ></i>
      <i class="fa-solid fa-bolt fa-xs w-3 basis-3 shrink-0" v-else></i>
      <span class="text-xs basis-4 shrink-0">
        <GenericStateDisplay
          :state="skill.currentState!"
          :minimal="true"
        ></GenericStateDisplay>
      </span>
      <span class="text-base">
        <SkillNameDisplay :skill="skill"></SkillNameDisplay>
      </span>
    </RouterLink>
    <span v-else class="text-pink-400 text-xs"> N/A: {{ nodeId }} </span>
  </div>
</template>

<style scoped>
.machine-link {
  display: flex;
  flex-direction: row;
  column-gap: 0.5rem;
  justify-content: flex-start;
  align-items: center;
  cursor: pointer;
}

.machine-link.router-link-active {
  @apply font-bold;
}

.machine-link:hover {
  @apply text-secondary;
}
</style>
