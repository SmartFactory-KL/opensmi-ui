<script setup lang="ts">
import Navigation from "./components/page-components/navigation/Navigation.vue";
import TitleBar from "./components/page-components/titlebar/TitleBar.vue";

import PinModal from "./components/page-components/pin-guard/PinModal.vue";
</script>

<template>
  <div class="main-view">
    <PinModal></PinModal>
    <TitleBar></TitleBar>
    <div class="main-navigation">
      <Navigation></Navigation>
    </div>
    <div class="main-container">
      <div class="main-content">
        <RouterView :key="$route.fullPath"></RouterView>
      </div>
      <div class="main-footer"></div>
    </div>
  </div>
</template>

<style scoped>
.main-view {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  margin: 0;
  margin-top: 4rem;
  width: 100vw;
  height: calc(100vh - 4rem);
  justify-content: stretch;
  align-items: stretch;
}

.main-container {
  @apply bg-gray-200 text-gray-900;
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  justify-content: stretch;
  align-items: stretch;
  width: 100%;
  height: 100%;
  overflow: auto;
}

.main-content {
  width: 100%;
  height: 100%;
  flex-grow: 1;
}
</style>
