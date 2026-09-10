<script lang="ts" setup>
defineProps<{
  component: ComponentDto;
}>();
</script>

<template>
  <RouterLink class="machine-link" :to="'/component/' + component.entityId">
    <i class="fa-solid fa-toolbox fa-xs"></i>
    <span class="text-base">{{ component.name }}</span>
    <span class="text-xs text-gray-400 pt-1">{{ component.currentState }}</span>
  </RouterLink>
</template>

<style scoped>
.machine-link {
  display: flex;
  flex-direction: row;
  column-gap: 0.3rem;
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
