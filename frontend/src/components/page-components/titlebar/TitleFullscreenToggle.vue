<script lang="ts" setup>
import { ref } from "vue";

const isFullscreen = ref(document.fullscreenElement !== null);

function toggleFullscreen() {
  if (!document.fullscreenEnabled) {
    return;
  }

  if (!document.fullscreenElement) {
    isFullscreen.value = true;
    document.documentElement.requestFullscreen();
  } else {
    isFullscreen.value = false;
    document.exitFullscreen();
  }
}
</script>

<template>
  <div
    class="flex flex-col justify-start items-center border border-secondary p-2 m-4"
    @click="toggleFullscreen"
  >
    <div
      class="flex flex-row jusitfy-start items-center"
      style="height: 2rem; width: 2rem"
    >
      <div class="button-settings" :class="{ active: isFullscreen }">
        <i class="fa-solid fa-expand fa-xl" v-show="!isFullscreen"></i>
        <i class="fa-solid fa-compress fa-xl" v-show="isFullscreen"></i>
      </div>
    </div>
    <div class="text-xs">
      <span v-show="!isFullscreen">Enter</span>
      <span v-show="isFullscreen">Exit</span>
    </div>
    <div class="text-xs">Fullscreen</div>
  </div>
</template>

<style scoped>
.button-settings {
  @apply flex flex-row justify-end items-center h-full mx-2 hover:scale-110 cursor-pointer;
}

.button-settings.active {
  @apply text-secondary;
}
</style>
