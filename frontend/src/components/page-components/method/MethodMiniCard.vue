<script setup lang="ts">
import GenericStateText from "../../GenericStateText.vue";

defineProps<{
  method: MethodDto;
}>();
</script>

<template>
  <div class="skill-mini-card">
    <RouterLink
      :to="'/skill/' + method.entityId"
      class="machine-link flex flex-row justify-start items-center gap-x-2"
    >
      <i class="fa-solid fa-minus fa-2xs"></i>
      <i class="fa-solid fa-bolt fa-xs"></i> {{ method.name }}
      <span class="text-gray-400">|</span>
      <GenericStateText state="open"></GenericStateText>
    </RouterLink>
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
  @apply text-secondary translate-x-1;
}
</style>
