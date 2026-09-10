<script lang="ts" setup>
defineProps<{
  method: MethodDto | undefined;
}>();
</script>

<template>
  <div>
    <RouterLink
      v-if="method"
      class="machine-link"
      :to="'/method/' + method.entityId"
    >
      <i class="fa-solid fa-meteor fa-xs w-3 basis-3 shrink-0"></i>
      <span class="text-base">{{ method.name }}</span>
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
  @apply text-secondary;
}
</style>
