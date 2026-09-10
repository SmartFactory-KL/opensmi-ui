<script lang="ts" setup>
import { ref } from "vue";
import { RouterLink } from "vue-router";

import { usePageStore } from "../../../stores/PageStore";
import TitleFullscreenToggle from "./TitleFullscreenToggle.vue";

const showSettings = ref(false);

const pageStore = usePageStore();
</script>

<template>
  <div class="flex flex-row jusitfy-start items-center">
    <div
      class="title-settings"
      @click="showSettings = !showSettings"
      :class="{ active: showSettings }"
    >
      <i class="fa-solid fa-gear fa-xl"></i>
    </div>
    <div class="title-settings-content" v-show="showSettings">
      <div class="flex flex-row justify-between items-center">
        <TitleFullscreenToggle></TitleFullscreenToggle>
        <div class="flex flex-col justify-center items-end gap-y-2">
          <span
            v-for="(flagValue, flagName) in pageStore.showFlags"
            @click="pageStore.showFlags[flagName] = !flagValue"
            class="hover:scale-105 cursor-pointer"
          >
            <span class="mr-4">{{ flagName }}</span>
            <i
              class="fa-solid fa-toggle-on fa-xl"
              v-show="flagValue == true"
            ></i>
            <i
              class="fa-solid fa-toggle-off fa-xl"
              v-show="flagValue != true"
            ></i>
          </span>
        </div>
      </div>
      <div
        class="mt-4 p-2 border text-xs hover:text-secondary hover:border-secondary hover:bg-white cursor-pointer"
      >
        <RouterLink
          to="/debug-info"
          @click="showSettings = false"
          >Show Debug Info</RouterLink
        >
      </div>
    </div>
  </div>
</template>

<style scoped>
.title-settings {
  @apply flex flex-row justify-end items-center h-full mx-2 hover:scale-105 cursor-pointer;
}

.title-settings.active i {
  @apply text-secondary;
}

.title-settings-content {
  @apply flex flex-col justify-between items-center ml-4 bg-primary p-4 border-4 border-secondary;
  position: fixed;
  right: 0;
  top: 4rem;
  z-index: 10;
  min-width: 22rem;
}
</style>
