<script lang="ts" setup>
defineProps<{
  messageCount: number;
}>();
</script>

<template>
  <div class="flex flex-col justify-center items-center gap-x-2">
    <div
      class="animate-heartbeat text-pink-400"
      :style="{
        animationDuration: `${Math.max(60.0 / messageCount, 0.2)}s`,
      }"
    >
      <i class="fa-solid fa-heart-pulse"></i>
    </div>
    <span>
      <i class="fa-solid fa-arrow-down"></i>
      {{ messageCount }}
    </span>
  </div>
</template>

<style scoped>
@keyframes heartbeat {
  0% {
    transform: scale(1);
  }
  75% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.animate-heartbeat {
  animation: heartbeat infinite ease-in-out;
}
</style>
